"use client";

import { memo, useEffect, useMemo, useRef, useState } from "react";
import {
  Background,
  Handle,
  MarkerType,
  Position,
  ReactFlow,
  type Edge,
  type Node,
  type NodeProps,
} from "@xyflow/react";

import type { RecommendationItem } from "@/lib/types";

type ActivityMeta = {
  code: string;
  name: string;
  phase: "Phase A" | "Phase B" | "Phase C";
  description: string;
};

type ActivityNodeData = {
  activity: ActivityMeta;
  status: "primary" | "secondary" | "default";
  stepLabel: string | null;
};

type Props = {
  recommendations: RecommendationItem[];
};

const ACTIVITY_MAP: Record<string, ActivityMeta> = {
  VAL: {
    code: "VAL",
    name: "Knowdell Values",
    phase: "Phase A",
    description: "Clarifies your core career values so decisions align with what matters most.",
  },
  STR: {
    code: "STR",
    name: "CliftonStrengths",
    phase: "Phase A",
    description: "Identifies natural strengths you can build into confident career direction.",
  },
  SKL: {
    code: "SKL",
    name: "Skillset Card Sort",
    phase: "Phase A",
    description: "Helps you name transferable skills and gaps from your experiences.",
  },
  NRG: {
    code: "NRG",
    name: "Energy Mapping",
    phase: "Phase B",
    description: "Tracks what energizes or drains you to ground decisions in daily reality.",
  },
  AI: {
    code: "AI",
    name: "AI Exploration Generator",
    phase: "Phase C",
    description: "Uses guided reflection to generate career pathways from your self-knowledge.",
  },
  MM: {
    code: "MM",
    name: "Mind Mapping",
    phase: "Phase C",
    description: "Expands possibilities through structured, creative exploration of pathways.",
  },
  DM: {
    code: "DM",
    name: "Decision Matrix",
    phase: "Phase C",
    description: "Compares options across practical factors to support clear decisions.",
  },
};

const NAME_TO_CODE = Object.fromEntries(
  Object.values(ACTIVITY_MAP).map((activity) => [activity.name, activity.code]),
) as Record<string, string>;

function ActivityNode({ data }: NodeProps<Node<ActivityNodeData, "activity">>) {
  const nodeClass =
    data.status === "primary"
      ? "flow-node-selected"
      : data.status === "secondary"
        ? "flow-node-secondary"
        : "flow-node-muted";

  return (
    <article className={`flow-node ${nodeClass}`}>
      <Handle type="target" position={Position.Top} className="flow-handle" />
      {data.stepLabel ? <span className="flow-node-step">{data.stepLabel}</span> : null}
      <span className="flow-node-phase">{data.activity.phase}</span>
      <h3>{data.activity.name}</h3>
      <Handle type="source" position={Position.Bottom} className="flow-handle" />
    </article>
  );
}

const nodeTypes = { activity: memo(ActivityNode) };

export function ResultsFlowDiagram({ recommendations }: Props): JSX.Element {
  const [hovered, setHovered] = useState<{ code: string; x: number; y: number } | null>(null);
  const [routeStage, setRouteStage] = useState(0);
  const canvasRef = useRef<HTMLDivElement>(null);

  const selectedCodes = useMemo(() => {
    const set = new Set<string>();
    for (const recommendation of recommendations) {
      const code = NAME_TO_CODE[recommendation.name];
      if (code) {
        set.add(code);
      }
    }
    return set;
  }, [recommendations]);

  const primaryRoute = useMemo(() => {
    const phaseARecommendations = recommendations.filter((item) => item.phase === "Phase A");
    const phaseCRecommendations = recommendations.filter((item) => item.phase === "Phase C");

    const topPhaseA = phaseARecommendations
      .map((item) => NAME_TO_CODE[item.name])
      .find((code): code is string => Boolean(code));
    const topPhaseC = phaseCRecommendations
      .map((item) => NAME_TO_CODE[item.name])
      .find((code): code is string => Boolean(code));
    const hasEnergyMapping = selectedCodes.has("NRG");

    return {
      topPhaseA,
      hasEnergyMapping,
      topPhaseC,
    };
  }, [recommendations, selectedCodes]);

  const nodes = useMemo<Array<Node<ActivityNodeData>>>(() => {
    const coords: Record<string, { x: number; y: number }> = {
      VAL: { x: 60, y: 60 },
      STR: { x: 420, y: 60 },
      SKL: { x: 780, y: 60 },
      NRG: { x: 420, y: 320 },
      AI: { x: 60, y: 580 },
      MM: { x: 420, y: 580 },
      DM: { x: 780, y: 580 },
    };

    return Object.values(ACTIVITY_MAP).map((activity) => ({
      id: activity.code,
      type: "activity",
      position: coords[activity.code],
      data: {
        activity,
        status: selectedCodes.has(activity.code) ? "secondary" : "default",
        stepLabel: null,
      },
      draggable: false,
      selectable: false,
    }));
  }, [selectedCodes]);

  const routeSequence = useMemo<string[]>(() => {
    const sequence: string[] = [];
    if (primaryRoute.topPhaseA) {
      sequence.push(primaryRoute.topPhaseA);
    }
    if (primaryRoute.hasEnergyMapping) {
      sequence.push("NRG");
    }
    if (primaryRoute.topPhaseC) {
      sequence.push(primaryRoute.topPhaseC);
    }
    return sequence;
  }, [primaryRoute]);

  useEffect(() => {
    setRouteStage(0);
    if (routeSequence.length === 0) {
      return;
    }

    let cancelled = false;
    routeSequence.forEach((_, index) => {
      window.setTimeout(() => {
        if (!cancelled) {
          setRouteStage(index + 1);
        }
      }, 240 * (index + 1));
    });

    return () => {
      cancelled = true;
    };
  }, [routeSequence]);

  const highlightedCodes = useMemo(() => new Set(routeSequence.slice(0, routeStage)), [routeSequence, routeStage]);

  const edges = useMemo<Array<Edge>>(() => {
    const baseEdges: Array<{ id: string; source: string; target: string }> = [
      { id: "VAL-NRG", source: "VAL", target: "NRG" },
      { id: "STR-NRG", source: "STR", target: "NRG" },
      { id: "SKL-NRG", source: "SKL", target: "NRG" },
      { id: "NRG-AI", source: "NRG", target: "AI" },
      { id: "NRG-MM", source: "NRG", target: "MM" },
      { id: "NRG-DM", source: "NRG", target: "DM" },
    ];

    return baseEdges.map((edge) => {
      const isAtoB = edge.target === "NRG";
      const isBtoC = edge.source === "NRG";

      const selected =
        (isAtoB &&
          edge.source === primaryRoute.topPhaseA &&
          highlightedCodes.has(edge.source) &&
          highlightedCodes.has("NRG")) ||
        (isBtoC &&
          edge.target === primaryRoute.topPhaseC &&
          highlightedCodes.has("NRG") &&
          highlightedCodes.has(edge.target));

      return {
        ...edge,
        type: "smoothstep",
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 18,
          height: 18,
          color: selected ? "#00693E" : "#A5D75F",
        },
        animated: selected,
        style: {
          strokeWidth: selected ? 3 : 2,
          stroke: selected ? "#00693E" : "#A5D75F",
        },
      };
    });
  }, [highlightedCodes, primaryRoute]);

  const displayedNodes = useMemo(
    () =>
      nodes.map((node) => ({
        ...node,
        data: {
          ...node.data,
          status: highlightedCodes.has(node.id)
            ? "primary"
            : selectedCodes.has(node.id)
              ? "secondary"
              : "default",
          stepLabel: routeSequence[0] === node.id ? "Step 1" : routeSequence[1] === node.id ? "Step 2" : routeSequence[2] === node.id ? "Step 3" : null,
        },
      })),
    [nodes, highlightedCodes, selectedCodes, routeSequence],
  );

  const hoveredActivity = hovered ? ACTIVITY_MAP[hovered.code] : null;

  function updateHover(nodeId: string, clientX: number, clientY: number): void {
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }
    const bounds = canvas.getBoundingClientRect();
    setHovered({
      code: nodeId,
      x: clientX - bounds.left + 14,
      y: clientY - bounds.top + 14,
    });
  }

  return (
    <div className="flow-shell" role="region" aria-label="Career activity flowchart">
      <div className="flow-legend" aria-hidden="true">
        <span><i className="legend-dot legend-dot-selected" /> Primary sequence</span>
        <span><i className="legend-dot legend-dot-secondary" /> Also recommended</span>
        <span><i className="legend-dot legend-dot-muted" /> Not selected</span>
      </div>
      <p className="flow-legend-text">
        Dark green shows your primary path. Light green cards are additional recommended options.
      </p>

      <div className="flow-canvas" ref={canvasRef}>
        <ReactFlow
          nodes={displayedNodes}
          edges={edges}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.18 }}
          nodesConnectable={false}
          nodesDraggable={false}
          zoomOnScroll={false}
          zoomOnPinch={false}
          zoomOnDoubleClick={false}
          panOnDrag={false}
          onNodeMouseEnter={(event, node) => updateHover(node.id, event.clientX, event.clientY)}
          onNodeMouseMove={(event, node) => updateHover(node.id, event.clientX, event.clientY)}
          onNodeMouseLeave={() => setHovered(null)}
        >
          <Background color="#E5F3ED" gap={28} size={1} />
        </ReactFlow>

        {hovered && hoveredActivity ? (
          <aside className="flow-tooltip" style={{ left: hovered.x, top: hovered.y }} aria-live="polite">
            <p className="roadmap-kicker">{hoveredActivity.phase}</p>
            <h3>{hoveredActivity.name}</h3>
            <p>{hoveredActivity.description}</p>
          </aside>
        ) : null}
      </div>
    </div>
  );
}
