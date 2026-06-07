import BodySilhouette from '../body/BodySilhouette';

export default function FitVisualization({ regions, gender }) {
  const regionScores = {};
  for (const r of regions) {
    if (r.score >= 80) regionScores[r.name] = 'green';
    else if (r.score >= 60) regionScores[r.name] = 'yellow';
    else regionScores[r.name] = 'red';
  }

  return <BodySilhouette gender={gender} regionScores={regionScores} />;
}
