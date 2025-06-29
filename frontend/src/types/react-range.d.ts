declare module 'react-range' {
  import * as React from 'react';
  export interface RangeProps {
    step: number;
    min: number;
    max: number;
    values: number[];
    onChange: (values: number[]) => void;
    renderTrack: (props: { props: any; children: React.ReactNode }) => React.ReactNode;
    renderThumb: (props: { props: any; index: number }) => React.ReactNode;
  }
  export const Range: React.FC<Partial<RangeProps>>;
} 