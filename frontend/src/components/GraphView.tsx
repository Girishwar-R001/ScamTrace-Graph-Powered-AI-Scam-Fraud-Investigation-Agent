import React, { useState, useEffect, useRef } from 'react';
import type { GraphData, GraphNode } from '../types';
import { ZoomIn, ZoomOut, RotateCcw, X, Shield, Phone, Globe, Wallet, AlertOctagon, FileText } from 'lucide-react';

interface GraphViewProps {
  graphData: GraphData;
  targetId?: string;
}

interface NodePosition {
  x: number;
  y: number;
  vx: number;
  vy: number;
}

// Enterprise Palantir/Datadog-grade semantic node themes
const LABEL_THEMES: Record<string, { bg: string; border: string; text: string; dot: string }> = {
  Phone: { bg: '#172033', border: '#3b82f6', text: '#bfdbfe', dot: '#3b82f6' },
  Domain: { bg: '#0f293a', border: '#0284c7', text: '#bae6fd', dot: '#0284c7' },
  Account: { bg: '#2b2114', border: '#d97706', text: '#fde68a', dot: '#d97706' },
  ScamCampaign: { bg: '#2d1519', border: '#e11d48', text: '#fecdd3', dot: '#e11d48' },
  Report: { bg: '#2b1b14', border: '#ea580c', text: '#ffedd5', dot: '#ea580c' },
  Evidence: { bg: '#12261e', border: '#10b981', text: '#a7f3d0', dot: '#10b981' },
  Default: { bg: '#1c202a', border: '#4b5568', text: '#cbd5e1', dot: '#4b5568' }
};

export const GraphView: React.FC<GraphViewProps> = ({ graphData, targetId }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [positions, setPositions] = useState<Record<string, NodePosition>>({});
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [zoom, setZoom] = useState<number>(1);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [draggedNodeId, setDraggedNodeId] = useState<string | null>(null);

  // Initialize and simulate relaxed force layout
  useEffect(() => {
    const nodes = graphData.nodes;
    const edges = graphData.edges;
    if (nodes.length === 0) return;

    const width = 840;
    const height = 520;
    const centerX = width / 2;
    const centerY = height / 2;

    const newPos: Record<string, NodePosition> = {};
    const radius = Math.min(width, height) * 0.38;

    nodes.forEach((n, idx) => {
      const angle = (idx / nodes.length) * 2 * Math.PI;
      const isTarget = targetId && (n.id === targetId || n.number === targetId || n.domain_name === targetId);
      newPos[n.id] = {
        x: isTarget ? centerX : centerX + radius * Math.cos(angle) + (Math.random() - 0.5) * 20,
        y: isTarget ? centerY : centerY + radius * Math.sin(angle) + (Math.random() - 0.5) * 20,
        vx: 0,
        vy: 0
      };
    });

    // Run relaxed spring simulation to ensure generous separation
    for (let iter = 0; iter < 90; iter++) {
      // Repulsion between all nodes
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const idA = nodes[i].id;
          const idB = nodes[j].id;
          const pA = newPos[idA];
          const pB = newPos[idB];
          if (!pA || !pB) continue;

          const dx = pB.x - pA.x;
          const dy = pB.y - pA.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          if (dist < 240) {
            const force = ((240 - dist) / dist) * 0.16;
            pA.x -= dx * force;
            pA.y -= dy * force;
            pB.x += dx * force;
            pB.y += dy * force;
          }
        }
      }

      // Spring attraction along edges
      edges.forEach((e) => {
        const pA = newPos[e.source];
        const pB = newPos[e.target];
        if (!pA || !pB) return;

        const dx = pB.x - pA.x;
        const dy = pB.y - pA.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const targetDist = 160;
        const force = (dist - targetDist) * 0.035;
        pA.x += (dx / dist) * force;
        pA.y += (dy / dist) * force;
        pB.x -= (dx / dist) * force;
        pB.y -= (dy / dist) * force;
      });

      // Subtle centering gravity
      nodes.forEach((n) => {
        const p = newPos[n.id];
        if (p) {
          p.x += (centerX - p.x) * 0.015;
          p.y += (centerY - p.y) * 0.015;
        }
      });
    }

    setPositions(newPos);
  }, [graphData, targetId]);

  // Pan / Canvas drag
  const handleMouseDown = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).tagName === 'svg' || (e.target as HTMLElement).id === 'graph-canvas') {
      setIsDragging(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
    } else if (draggedNodeId && positions[draggedNodeId]) {
      const rect = containerRef.current?.getBoundingClientRect();
      if (!rect) return;
      const mouseX = (e.clientX - rect.left - pan.x) / zoom;
      const mouseY = (e.clientY - rect.top - pan.y) / zoom;
      setPositions((prev) => ({
        ...prev,
        [draggedNodeId]: { ...prev[draggedNodeId], x: mouseX, y: mouseY }
      }));
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    setDraggedNodeId(null);
  };

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'Phone': return <Phone className="w-3.5 h-3.5" />;
      case 'Domain': return <Globe className="w-3.5 h-3.5" />;
      case 'Account': return <Wallet className="w-3.5 h-3.5" />;
      case 'ScamCampaign': return <AlertOctagon className="w-3.5 h-3.5" />;
      case 'Report': return <FileText className="w-3.5 h-3.5" />;
      case 'Evidence': return <Shield className="w-3.5 h-3.5" />;
      default: return null;
    }
  };

  const getNodeTitle = (n: GraphNode) => {
    if (n.number) return n.number;
    if (n.domain_name) return n.domain_name;
    if (n.account_id) return n.account_id;
    if (n.campaign_id) return n.name || n.campaign_id;
    if (n.report_id) return n.report_id;
    if (n.evidence_id) return n.evidence_id;
    return n.id;
  };

  return (
    <div
      ref={containerRef}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      className="relative w-full h-[540px] bg-[#12141b] select-none overflow-hidden"
    >
      {/* Background Subtle Coordinate Grid */}
      <div 
        className="absolute inset-0 pointer-events-none opacity-20"
        style={{
          backgroundImage: 'radial-gradient(circle, #303748 1px, transparent 1px)',
          backgroundSize: '24px 24px'
        }}
      />

      {/* Minimal Zoom & View Controls */}
      <div className="absolute top-3 right-3 flex items-center bg-[#181b24] border border-[#2b3040] rounded-md p-0.5 shadow-md z-20">
        <button
          onClick={() => setZoom((z) => Math.min(z * 1.25, 2.5))}
          className="p-1.5 rounded text-[#9ba3b4] hover:text-[#e8eaf0] hover:bg-[#252a38] transition-colors"
          title="Zoom in"
        >
          <ZoomIn className="w-3.5 h-3.5" />
        </button>
        <button
          onClick={() => setZoom((z) => Math.max(z * 0.8, 0.4))}
          className="p-1.5 rounded text-[#9ba3b4] hover:text-[#e8eaf0] hover:bg-[#252a38] transition-colors"
          title="Zoom out"
        >
          <ZoomOut className="w-3.5 h-3.5" />
        </button>
        <div className="w-px h-3.5 bg-[#2b3040] mx-0.5" />
        <button
          onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }); }}
          className="p-1.5 rounded text-[#9ba3b4] hover:text-[#e8eaf0] hover:bg-[#252a38] transition-colors"
          title="Reset canvas"
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* SVG Canvas */}
      <svg
        id="graph-canvas"
        className="w-full h-full cursor-grab active:cursor-grabbing"
        style={{ transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`, transformOrigin: 'center' }}
      >
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="24" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#3e4659" />
          </marker>
          <marker id="arrow-highlight" viewBox="0 0 10 10" refX="25" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#5e81f4" />
          </marker>
        </defs>

        {/* Relationship Edges */}
        {graphData.edges.map((e, idx) => {
          const pA = positions[e.source];
          const pB = positions[e.target];
          if (!pA || !pB) return null;

          const isHighlighted = Boolean(e.highlight);
          const isRelatedToHover = hoveredNodeId === e.source || hoveredNodeId === e.target;
          const isRelatedToSelected = selectedNode?.id === e.source || selectedNode?.id === e.target;
          const activeEdge = isHighlighted || isRelatedToHover || isRelatedToSelected;

          const midX = (pA.x + pB.x) / 2;
          const midY = (pA.y + pB.y) / 2;

          return (
            <g key={`edge-${idx}`}>
              <line
                x1={pA.x}
                y1={pA.y}
                x2={pB.x}
                y2={pB.y}
                stroke={activeEdge ? '#5e81f4' : '#2b3142'}
                strokeWidth={activeEdge ? 2 : 1.25}
                strokeDasharray={isHighlighted ? '4 3' : 'none'}
                markerEnd={activeEdge ? 'url(#arrow-highlight)' : 'url(#arrow)'}
              />
              {/* Relationship label with clear halo background */}
              <text
                x={midX}
                y={midY - 4}
                fill={activeEdge ? '#93c5fd' : '#717a8c'}
                fontSize="9px"
                fontFamily="JetBrains Mono, monospace"
                textAnchor="middle"
                stroke="#12141b"
                strokeWidth={3}
                paintOrder="stroke"
                className="select-none pointer-events-none"
              >
                {e.type}
              </text>
            </g>
          );
        })}

        {/* Nodes */}
        {graphData.nodes.map((n) => {
          const pos = positions[n.id];
          if (!pos) return null;

          const label = n.label || (n as any)._label || 'Entity';
          const theme = LABEL_THEMES[label] || LABEL_THEMES.Default;
          const isTarget = targetId && (n.id === targetId || n.number === targetId || n.domain_name === targetId);
          const isSelected = selectedNode?.id === n.id;
          const isHovered = hoveredNodeId === n.id;
          const nodeRadius = isTarget ? 21 : 17;
          const title = getNodeTitle(n);

          return (
            <g
              key={n.id}
              transform={`translate(${pos.x}, ${pos.y})`}
              className="cursor-pointer"
              onMouseEnter={() => setHoveredNodeId(n.id)}
              onMouseLeave={() => setHoveredNodeId(null)}
              onMouseDown={(e) => {
                e.stopPropagation();
                setDraggedNodeId(n.id);
              }}
              onClick={() => setSelectedNode(n)}
            >
              {/* Restrained Target Ring (Clean solid highlight, zero animation) */}
              {isTarget && (
                <circle
                  r={nodeRadius + 4}
                  fill="none"
                  stroke="#5e81f4"
                  strokeWidth={1.5}
                  strokeOpacity={0.7}
                />
              )}

              {/* Selection Ring */}
              {isSelected && (
                <circle
                  r={nodeRadius + 4}
                  fill="none"
                  stroke="#ffffff"
                  strokeWidth={1.5}
                />
              )}

              {/* Node Body */}
              <circle
                r={nodeRadius}
                fill={theme.bg}
                stroke={isTarget ? '#5e81f4' : isSelected ? '#ffffff' : isHovered ? '#94a3b8' : theme.border}
                strokeWidth={isTarget || isSelected ? 2 : 1.5}
              />

              {/* Node Type Label */}
              <text
                x={0}
                y={3.5}
                textAnchor="middle"
                fill="#ffffff"
                fontSize={isTarget ? '10px' : '9px'}
                fontWeight="600"
                fontFamily="Inter, sans-serif"
                className="select-none pointer-events-none"
              >
                {label.substring(0, 3).toUpperCase()}
              </text>

              {/* Node Title with Halo */}
              <text
                x={0}
                y={nodeRadius + 14}
                textAnchor="middle"
                fill={isTarget ? '#93c5fd' : isSelected ? '#ffffff' : '#cbd5e1'}
                fontSize="11px"
                fontWeight={isTarget || isSelected ? '600' : '500'}
                fontFamily="Inter, sans-serif"
                stroke="#12141b"
                strokeWidth={3}
                paintOrder="stroke"
                className="select-none pointer-events-none"
              >
                {title.length > 26 ? title.substring(0, 24) + '…' : title}
              </text>

              {/* Risk Score */}
              {n.risk_score !== undefined && (
                <text
                  x={0}
                  y={nodeRadius + 26}
                  textAnchor="middle"
                  fill={n.risk_score > 0.7 ? '#f87171' : n.risk_score < 0.2 ? '#34d399' : '#fbbf24'}
                  fontSize="9.5px"
                  fontFamily="JetBrains Mono, monospace"
                  stroke="#12141b"
                  strokeWidth={2.5}
                  paintOrder="stroke"
                  className="select-none pointer-events-none"
                >
                  risk: {n.risk_score}
                </text>
              )}
            </g>
          );
        })}
      </svg>

      {/* Compact Understated Legend */}
      <div className="absolute bottom-3 left-3 bg-[#161820]/90 backdrop-blur-sm px-3 py-1.5 rounded-md border border-[#272b37] text-xs z-10 hidden sm:flex items-center gap-3">
        <span className="text-[11px] font-medium text-[#6b7280]">Entities:</span>
        {Object.entries(LABEL_THEMES).filter(([k]) => k !== 'Default').map(([lbl, theme]) => (
          <div key={lbl} className="flex items-center gap-1.5">
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: theme.dot }}
            />
            <span className="text-[#9ba3b4] text-[11px] font-mono">{lbl}</span>
          </div>
        ))}
      </div>

      {/* Selected Node Details Inspector Panel */}
      {selectedNode && (
        <div className="absolute top-3 left-3 w-80 max-h-[480px] bg-[#161820] border border-[#2b3040] rounded-lg p-4 z-30 shadow-xl overflow-y-auto">
          <div className="flex items-center justify-between pb-2.5 border-b border-[#242835] mb-3">
            <div className="flex items-center gap-2">
              <span className="text-[#5e81f4]">
                {getNodeIcon(selectedNode.label || selectedNode._label || '')}
              </span>
              <span className="text-xs font-semibold text-[#e8eaf0]">
                {selectedNode.label || selectedNode._label || 'Entity Record'}
              </span>
            </div>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-[#6b7280] hover:text-[#e8eaf0] p-0.5 rounded hover:bg-[#222634] transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-2.5 text-xs">
            <div className="bg-[#12141a] p-2.5 rounded border border-[#242835] font-mono text-xs text-[#93c5fd] font-medium break-all">
              {getNodeTitle(selectedNode)}
            </div>

            <div className="space-y-1.5">
              {Object.entries(selectedNode)
                .filter(([k]) => !k.startsWith('_') && k !== 'id')
                .map(([key, val]) => (
                  <div key={key} className="flex items-baseline justify-between gap-2 py-1 border-b border-[#1f232e] text-[11.5px]">
                    <span className="text-[#6b7280] font-mono">{key}:</span>
                    <span className="text-[#d1d5db] font-mono text-right break-all">
                      {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                    </span>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GraphView;
