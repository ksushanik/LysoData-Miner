#!/usr/bin/env python3
import os
import sys
import re
import argparse
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, func, or_
from dotenv import load_dotenv
from collections import defaultdict
import networkx as nx

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app.models import Strain, CollectionNumber, StrainCollection

# Construct DATABASE_URL from individual environment variables
DB_USER = os.getenv("DB_USER", "lysobacter_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "lysobacter_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5434")
DB_NAME = os.getenv("DB_NAME", "lysobacter_db")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise ValueError("One or more database environment variables are not set. Please check your .env file.")

# Regex to find common collection prefixes and numbers
# Examples: ATCC 29489T, DSM6980T, LMG 8763T, JCM 18257T
COLLECTION_REGEX = re.compile(
    r'\b((?:ATCC|DSM|LMG|JCM|VKM|CCUG|NBRC|KACC|BCRC|KCTC|CCTCC|UASM|IMMIB|CECT)\s*[\d-]+\s*T?)\b',
    re.IGNORECASE
)

# --- Helper Functions ---
def normalize_collection_identifier(identifier: str) -> str:
    """Normalizes 'DSM 123' to 'DSM123' for consistent comparison."""
    return "".join(identifier.split()).upper()

def parse_code_and_number(identifier: str) -> tuple[str, str]:
    """Splits 'ATCC 29489T' into ('ATCC', '29489T')."""
    match = re.match(r'([A-Z]+)\s*([\d-]+T?)', identifier, re.IGNORECASE)
    if match:
        return match.groups()
    # Fallback for identifiers without spaces like 'DSM6980T'
    match = re.match(r'([A-Z]+)([\d-]+T?)', identifier, re.IGNORECASE)
    if match:
        return match.groups()
    return identifier, ""

# --- Main Logic ---
async def normalize_strains(dry_run: bool):
    print("🚀 Starting strain normalization process...")
    engine = create_async_engine(str(DATABASE_URL), echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        try:
            # 1. Fetch all strains. We'll process them in memory.
            all_strains = (await session.execute(select(Strain))).scalars().all()
            strain_map = {strain.strain_id: strain for strain in all_strains}
            print(f"✅ Loaded {len(all_strains)} strains from the database.")

            # 2. Build a graph of relationships
            # Nodes are strain IDs. Edges connect strains that share a collection number.
            G = nx.Graph()
            G.add_nodes_from(strain_map.keys())
            
            # Map normalized collection number -> list of strain IDs
            collection_to_strains = defaultdict(list)

            for strain in all_strains:
                full_text = f"{strain.strain_identifier} {strain.notes or ''}"
                found_numbers = {normalize_collection_identifier(s) for s in COLLECTION_REGEX.findall(full_text)}
                for norm_id in found_numbers:
                    collection_to_strains[norm_id].append(strain.strain_id)

            # Add edges to the graph
            for strain_ids in collection_to_strains.values():
                if len(strain_ids) > 1:
                    for i in range(len(strain_ids)):
                        for j in range(i + 1, len(strain_ids)):
                            G.add_edge(strain_ids[i], strain_ids[j])

            # 3. Find connected components (these are our synonym groups)
            synonym_groups = [g for g in nx.connected_components(G) if len(g) > 1]
            print(f"🔍 Found {len(synonym_groups)} groups of synonymous strains.")
            
            if not synonym_groups:
                print("No synonym groups found. Nothing to do.")
                return

            if dry_run:
                print("\nDRY RUN MODE: No changes will be made to the database. Displaying plan:")
            
            # 4. Process each group
            for i, group in enumerate(synonym_groups):
                print(f"\n--- Group {i+1}/{len(synonym_groups)} ---")
                
                # a. Select a master strain
                group_strains = [strain_map[sid] for sid in group]
                master_strain = max(group_strains, key=lambda s: (
                    'master entry' in (s.notes or '').lower(),
                    'type strain' in (s.notes or '').lower(),
                    len(s.description or ''),
                    len(s.notes or '')
                ))
                duplicate_strains = [s for s in group_strains if s.strain_id != master_strain.strain_id]
                
                print(f"  👑 MASTER: Strain ID {master_strain.strain_id} ({master_strain.strain_identifier})")
                if duplicate_strains:
                    dup_ids = ', '.join([f"{s.strain_id} ({s.strain_identifier})" for s in duplicate_strains])
                    print(f"  🔗 SYNONYMS: {dup_ids}")

                # b. Consolidate all collection numbers from the group
                all_collection_ids = set()
                for strain in group_strains:
                    full_text = f"{strain.strain_identifier} {strain.notes or ''}"
                    all_collection_ids.update(COLLECTION_REGEX.findall(full_text))

                print(f"  📚 Collection IDs to consolidate: {', '.join(sorted(list(all_collection_ids)))}")

                # c. Plan database actions
                if not dry_run:
                    print("  ⚡ APPLYING CHANGES:")
                    # In a real run, transaction would start here
                    
                # i. Create/update CollectionNumber entries
                for identifier in sorted(list(all_collection_ids)):
                    code, number = parse_code_and_number(identifier)
                    
                    # Check if it exists
                    existing_cn = (await session.execute(
                        select(CollectionNumber).where(func.upper(CollectionNumber.collection_code) == code.upper(), CollectionNumber.collection_number == number)
                    )).scalar_one_or_none()
                    
                    if existing_cn:
                        print(f"    - Found existing CollectionNumber: {identifier} (ID: {existing_cn.collection_number_id})")
                        cn_id = existing_cn.collection_number_id
                    else:
                        print(f"    - CREATE CollectionNumber: {identifier}")
                        cn_id = -1 # Placeholder for dry run
                        if not dry_run:
                            new_cn = CollectionNumber(collection_code=code, collection_number=number)
                            session.add(new_cn)
                            await session.flush()
                            cn_id = new_cn.collection_number_id
                            print(f"      -> CREATED with ID: {cn_id}")

                    # ii. Link to master strain
                    if cn_id == -1 and not dry_run:
                         # This case should not happen if flush works, but as a safeguard
                         raise Exception(f"Could not get ID for new collection number {identifier}")
                    
                    # Check if link exists
                    existing_link = (await session.execute(
                        select(StrainCollection).where(StrainCollection.strain_id == master_strain.strain_id, StrainCollection.collection_number_id == cn_id)
                    )).scalar_one_or_none()

                    if existing_link:
                        print(f"    - Link already exists for Strain {master_strain.strain_id} and CN {identifier}")
                    else:
                        print(f"    - LINK Strain {master_strain.strain_id} to CN {identifier}")
                        if not dry_run:
                            if cn_id == -1:
                                print("       -> SKIPPING link due to missing CN ID in dry_run")
                                continue
                            new_link = StrainCollection(strain_id=master_strain.strain_id, collection_number_id=cn_id)
                            session.add(new_link)

                # iii. Mark duplicates
                for dup_strain in duplicate_strains:
                    new_note = f"DUPLICATE of Strain ID {master_strain.strain_id} ({master_strain.strain_identifier}). See master record for consolidated data.\nOriginal notes: {dup_strain.notes or ''}".strip()
                    print(f"    - MARK Strain {dup_strain.strain_id} as duplicate of {master_strain.strain_id}")
                    if not dry_run:
                        dup_strain.is_duplicate = True
                        dup_strain.master_strain_id = master_strain.strain_id
                        dup_strain.notes = new_note
                        session.add(dup_strain)

            if not dry_run:
                print("\nCommitting all changes to the database...")
                await session.commit()
                print("Changes committed.")
            else:
                print("\nDry run finished. No changes were made.")

        except Exception as e:
            print(f"❌ An error occurred: {e}")
            await session.rollback()
        finally:
            await engine.dispose()
    print("✅ Normalization process finished.")

async def main():
    parser = argparse.ArgumentParser(description="Normalize strain data by extracting collection numbers and merging duplicates.")
    parser.add_argument(
        '--apply',
        dest='dry_run',
        action='store_false',
        default=True,
        help="Apply changes to the database. Default is a dry run that shows the plan."
    )
    args = parser.parse_args()
    
    # Check for networkx
    try:
        import networkx
    except ImportError:
        print("❌ 'networkx' library is not installed. Please run: pip install networkx")
        sys.exit(1)

    await normalize_strains(dry_run=args.dry_run)

if __name__ == "__main__":
    asyncio.run(main()) 