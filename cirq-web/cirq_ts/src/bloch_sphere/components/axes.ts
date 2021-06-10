import {Vector3, LineBasicMaterial, BufferGeometry, Line} from 'three';

interface Axis {
  points: [Vector3, Vector3];
  hexColor: string;
  readonly lineWidth: number;
}

/**
 * Creates the x, y, and z axis for the Bloch sphere.
 * @param radius The overall radius of the bloch sphere.
 * @returns An object mapping the name of the axis to its corresponding
 * Line object to be rendered by the three.js scene.
 */
export function generateAxis(
  radius: number,
  xAxisColor = '#1f51ff',
  yAxisColor = '#ff3131',
  zAxisColor = '#39ff14'
) {
  const LINE_WIDTH = 1.5;
  const xPoints: [Vector3, Vector3] = [
    new Vector3(-radius, 0, 0),
    new Vector3(radius, 0, 0),
  ];
  const yPoints: [Vector3, Vector3] = [
    new Vector3(0, 0, -radius),
    new Vector3(0, 0, radius),
  ];
  const zPoints: [Vector3, Vector3] = [
    new Vector3(0, -radius, 0),
    new Vector3(0, radius, 0),
  ];
  return {
    x: asLine({points: xPoints, hexColor: xAxisColor, lineWidth: LINE_WIDTH}),
    y: asLine({points: yPoints, hexColor: yAxisColor, lineWidth: LINE_WIDTH}),
    z: asLine({points: zPoints, hexColor: zAxisColor, lineWidth: LINE_WIDTH}),
  };
}

function asLine(axis: Axis): Line {
  return new Line(
    new BufferGeometry().setFromPoints(axis.points),
    new LineBasicMaterial({color: axis.hexColor, linewidth: axis.lineWidth})
  );
}
