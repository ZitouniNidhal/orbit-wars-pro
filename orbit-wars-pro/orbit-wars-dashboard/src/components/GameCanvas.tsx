import React, { useRef, useEffect, useState } from 'react';
import { Planet, Fleet, Player } from '../types';
import { BOARD_SIZE, SUN_RADIUS, SUN_POSITION, PLAYER_COLORS } from '../utils/constants';

interface GameCanvasProps {
  planets: Planet[];
  fleets: Fleet[];
  players: Player[];
  currentPlayer: number;
  selectedPlanet: number | null;
  onPlanetSelect: (planetId: number | null) => void;
  plannedActions: Array<{ from: number; to: number; angle: number; ships: number }>;
}

const GameCanvas: React.FC<GameCanvasProps> = ({
  planets,
  fleets,
  players,
  currentPlayer,
  selectedPlanet,
  onPlanetSelect,
  plannedActions,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hoveredPlanet, setHoveredPlanet] = useState<number | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.fillStyle = '#0a0a1a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw grid
    ctx.strokeStyle = '#1a1a2e';
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= BOARD_SIZE; i += 10) {
      ctx.beginPath();
      ctx.moveTo(i * 6, 0);
      ctx.lineTo(i * 6, canvas.height);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(0, i * 6);
      ctx.lineTo(canvas.width, i * 6);
      ctx.stroke();
    }

    // Draw sun
    const sunX = SUN_POSITION[0] * 6;
    const sunY = SUN_POSITION[1] * 6;
    const sunRadius = SUN_RADIUS * 6;

    // Sun glow
    const gradient = ctx.createRadialGradient(sunX, sunY, 0, sunX, sunY, sunRadius * 2);
    gradient.addColorStop(0, 'rgba(255, 200, 50, 0.8)');
    gradient.addColorStop(0.5, 'rgba(255, 150, 30, 0.4)');
    gradient.addColorStop(1, 'rgba(255, 100, 0, 0)');
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(sunX, sunY, sunRadius * 2, 0, Math.PI * 2);
    ctx.fill();

    // Sun body
    ctx.fillStyle = '#ffcc33';
    ctx.beginPath();
    ctx.arc(sunX, sunY, sunRadius, 0, Math.PI * 2);
    ctx.fill();

    // Draw orbit paths for orbiting planets
    ctx.strokeStyle = 'rgba(100, 100, 150, 0.2)';
    ctx.lineWidth = 1;
    planets.forEach((planet) => {
      if (planet.angularVelocity !== 0) {
        const orbitRadius = Math.sqrt(
          Math.pow(planet.x - SUN_POSITION[0], 2) + Math.pow(planet.y - SUN_POSITION[1], 2)
        ) * 6;
        ctx.beginPath();
        ctx.arc(sunX, sunY, orbitRadius, 0, Math.PI * 2);
        ctx.stroke();
      }
    });

    // Draw planned fleet actions
    plannedActions.forEach((action) => {
      const fromPlanet = planets.find((p) => p.id === action.from);
      const toPlanet = planets.find((p) => p.id === action.to);
      if (fromPlanet && toPlanet) {
        ctx.strokeStyle = 'rgba(0, 255, 128, 0.6)';
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.moveTo(fromPlanet.x * 6, fromPlanet.y * 6);
        ctx.lineTo(toPlanet.x * 6, toPlanet.y * 6);
        ctx.stroke();
        ctx.setLineDash([]);

        // Arrow head
        const angle = Math.atan2(toPlanet.y * 6 - fromPlanet.y * 6, toPlanet.x * 6 - fromPlanet.x * 6);
        const arrowX = (fromPlanet.x * 6 + toPlanet.x * 6) / 2;
        const arrowY = (fromPlanet.y * 6 + toPlanet.y * 6) / 2;
        ctx.fillStyle = 'rgba(0, 255, 128, 0.8)';
        ctx.beginPath();
        ctx.moveTo(arrowX, arrowY);
        ctx.lineTo(arrowX - 10 * Math.cos(angle - 0.3), arrowY - 10 * Math.sin(angle - 0.3));
        ctx.lineTo(arrowX - 10 * Math.cos(angle + 0.3), arrowY - 10 * Math.sin(angle + 0.3));
        ctx.closePath();
        ctx.fill();
      }
    });

    // Draw fleets
    fleets.forEach((fleet) => {
      const x = fleet.x * 6;
      const y = fleet.y * 6;
      const color = PLAYER_COLORS[fleet.owner] || '#888';

      // Fleet trail
      const trailLength = 30;
      const trailX = x - Math.cos(fleet.angle) * trailLength;
      const trailY = y - Math.sin(fleet.angle) * trailLength;
      const trailGradient = ctx.createLinearGradient(trailX, trailY, x, y);
      trailGradient.addColorStop(0, 'transparent');
      trailGradient.addColorStop(1, color);
      ctx.strokeStyle = trailGradient;
      ctx.lineWidth = Math.max(2, fleet.ships / 50);
      ctx.beginPath();
      ctx.moveTo(trailX, trailY);
      ctx.lineTo(x, y);
      ctx.stroke();

      // Fleet body
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, Math.max(4, fleet.ships / 30), 0, Math.PI * 2);
      ctx.fill();

      // Fleet count
      ctx.fillStyle = '#fff';
      ctx.font = '10px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(fleet.ships.toString(), x, y + 3);
    });

    // Draw planets
    planets.forEach((planet) => {
      const x = planet.x * 6;
      const y = planet.y * 6;
      const radius = planet.radius * 6;
      const color =
        planet.owner === -1
          ? '#666'
          : planet.owner === currentPlayer
          ? PLAYER_COLORS[planet.owner]
          : PLAYER_COLORS[planet.owner] || '#888';

      // Planet glow
      if (planet.owner !== -1) {
        const glowGradient = ctx.createRadialGradient(x, y, radius, x, y, radius * 2);
        glowGradient.addColorStop(0, color + '66');
        glowGradient.addColorStop(1, 'transparent');
        ctx.fillStyle = glowGradient;
        ctx.beginPath();
        ctx.arc(x, y, radius * 2, 0, Math.PI * 2);
        ctx.fill();
      }

      // Planet body
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();

      // Planet border (selection/hover)
      if (planet.id === selectedPlanet || planet.id === hoveredPlanet) {
        ctx.strokeStyle = '#00ff88';
        ctx.lineWidth = 3;
        ctx.stroke();
      }

      // Ship count
      ctx.fillStyle = planet.owner === -1 ? '#fff' : '#000';
      ctx.font = 'bold 11px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(planet.ships.toString(), x, y + 4);

      // Production indicator
      ctx.fillStyle = '#aaa';
      ctx.font = '9px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(`+${planet.production}`, x, y + radius + 12);

      // Angular velocity indicator (orbiting)
      if (planet.angularVelocity !== 0) {
        ctx.fillStyle = '#00aaff';
        ctx.font = '8px monospace';
        ctx.fillText('⟳', x + radius + 5, y - 2);
      }
    });

    // Draw legend
    ctx.fillStyle = '#fff';
    ctx.font = '12px sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('Players:', 10, 20);
    players.forEach((player, index) => {
      ctx.fillStyle = PLAYER_COLORS[player.id] || '#888';
      ctx.fillRect(70 + index * 20, 12, 12, 12);
      ctx.fillStyle = '#fff';
      ctx.fillText(player.name || `P${player.id}`, 85 + index * 20, 22);
    });
  }, [planets, fleets, players, currentPlayer, selectedPlanet, hoveredPlanet, plannedActions]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) / 6;
    const y = (e.clientY - rect.top) / 6;

    // Find clicked planet
    const clickedPlanet = planets.find(
      (p) => Math.sqrt(Math.pow(p.x - x, 2) + Math.pow(p.y - y, 2)) <= p.radius + 2
    );

    onPlanetSelect(clickedPlanet?.id || null);
  };

  const handleCanvasMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) / 6;
    const y = (e.clientY - rect.top) / 6;

    const hovered = planets.find(
      (p) => Math.sqrt(Math.pow(p.x - x, 2) + Math.pow(p.y - y, 2)) <= p.radius + 2
    );

    setHoveredPlanet(hovered?.id || null);
  };

  return (
    <div className="relative">
      <canvas
        ref={canvasRef}
        width={BOARD_SIZE * 6}
        height={BOARD_SIZE * 6}
        className="border border-gray-700 rounded-lg cursor-pointer"
        onClick={handleCanvasClick}
        onMouseMove={handleCanvasMouseMove}
      />
      <div className="absolute top-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
        Click planet to select
      </div>
    </div>
  );
};

export default GameCanvas;
