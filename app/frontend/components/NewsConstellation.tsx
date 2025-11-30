"use client";

import React, { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { motion, AnimatePresence } from "framer-motion";
import type { GlobalItem, LocalTopic } from "../lib/mock";

type Props = {
    items: GlobalItem[];
};

type Node = d3.SimulationNodeDatum & {
    id: string;
    type: "MEGA" | "LOCAL";
    title: string;
    r: number;
    data: GlobalItem | LocalTopic;
    color: string;
    parent?: Node; // For local topics
};

type Link = d3.SimulationLinkDatum<Node>;

interface NewsConstellationProps {
    items: GlobalItem[];
    onNodeClick?: (item: GlobalItem | LocalTopic | null) => void;
}

export function NewsConstellation({ items, onNodeClick }: NewsConstellationProps) {
    const svgRef = useRef<SVGSVGElement>(null);
    // Remove internal selectedNode state if we want to control it from outside,
    // OR keep it for visual highlighting but use callback for details.
    // Let's keep internal state for D3 interaction but notify parent.
    const [selectedNode, setSelectedNode] = useState<GlobalItem | LocalTopic | null>(null);

    useEffect(() => {
        if (!svgRef.current || !items.length) return;

        const width = svgRef.current.clientWidth;
        const height = svgRef.current.clientHeight;

        // 1. Prepare Data
        const nodes: Node[] = [];
        const links: Link[] = [];

        items.forEach((mega) => {
            // Megatopic Node
            const megaNode: Node = {
                id: mega.id,
                type: "MEGA",
                title: mega.title_ko,
                r: 25 + (mega.article_count || 0) * 0.2, // Size based on importance
                data: mega,
                color: "#FBBF24", // Amber-400
                x: width / 2 + (Math.random() - 0.5) * 50,
                y: height / 2 + (Math.random() - 0.5) * 50,
            };
            nodes.push(megaNode);

            // Local Topic Nodes
            mega.localTopics?.forEach((local) => {
                const localNode: Node = {
                    id: local.id,
                    type: "LOCAL",
                    title: local.topic_name,
                    r: 8,
                    data: local,
                    color: "#60A5FA", // Blue-400
                    parent: megaNode,
                    x: megaNode.x! + (Math.random() - 0.5) * 20,
                    y: megaNode.y! + (Math.random() - 0.5) * 20,
                };
                nodes.push(localNode);
                links.push({ source: megaNode.id, target: localNode.id });
            });
        });

        // 2. Setup Simulation
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id((d: any) => d.id).distance(60).strength(0.5))
            .force("charge", d3.forceManyBody().strength(-100)) // Repel
            .force("collide", d3.forceCollide().radius((d: any) => d.r + 5).iterations(2)) // Prevent overlap
            .force("center", d3.forceCenter(width / 2, height / 2).strength(0.05))
            .force("x", d3.forceX(width / 2).strength(0.01))
            .force("y", d3.forceY(height / 2).strength(0.01));

        // 3. Render
        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove(); // Clear previous

        const g = svg.append("g"); // Container for zoom

        // Zoom behavior
        const zoom = d3.zoom<SVGSVGElement, unknown>()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {
                g.attr("transform", event.transform);
            });

        svg.call(zoom);

        // Links
        const link = g.append("g")
            .attr("stroke", "rgba(255,255,255,0.1)")
            .attr("stroke-width", 1)
            .selectAll("line")
            .data(links)
            .join("line");

        // Nodes
        const node = g.append("g")
            .selectAll("g")
            .data(nodes)
            .join("g")
            .attr("cursor", "pointer")
            .call(d3.drag<SVGGElement, Node>()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended) as any);

        // Circles
        node.append("circle")
            .attr("r", (d) => d.r)
            .attr("fill", (d) => d.color)
            .attr("stroke", "#fff")
            .attr("stroke-width", (d) => d.type === "MEGA" ? 2 : 1)
            .attr("opacity", 0.9)
            .on("click", (event, d) => {
                event.stopPropagation();
                // setSelectedNode(d);

                // Fly to node
                const scale = 2;
                const x = -d.x! * scale + width / 2;
                const y = -d.y! * scale + height / 2;
                svg.transition().duration(750).call(
                    zoom.transform,
                    d3.zoomIdentity.translate(x, y).scale(scale)
                );
            });

        // Labels (Only for Mega initially, or on zoom)
        const labels = node.append("text")
            .text((d) => d.type === "MEGA" ? d.title : "")
            .attr("x", 0)
            .attr("y", (d) => d.r + 15)
            .attr("text-anchor", "middle")
            .attr("fill", "white")
            .attr("font-size", "12px")
            .attr("font-weight", "bold")
            .attr("pointer-events", "none")
            .style("text-shadow", "0 2px 4px rgba(0,0,0,0.8)");

        // Simulation Tick
        simulation.on("tick", () => {
            link
                .attr("x1", (d: any) => d.source.x)
                .attr("y1", (d: any) => d.source.y)
                .attr("x2", (d: any) => d.target.x)
                .attr("y2", (d: any) => d.target.y);

            node.attr("transform", (d) => `translate(${d.x},${d.y})`);
        });

        // Drag functions
        function dragstarted(event: any, d: any) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event: any, d: any) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event: any, d: any) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }

        function handleNodeClick(event: any, d: Node) {
            event.stopPropagation();

            // Zoom logic
            const scale = 2;
            const x = -d.x! * scale + width / 2;
            const y = -d.y! * scale + height / 2;
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity.translate(x, y).scale(scale)
            );

            const item = d.type === 'MEGA'
                ? items.find(i => i.id === d.id)
                : items.flatMap(i => i.localTopics || []).find(t => t?.id === d.id);

            // setSelectedNode(item || null); // REMOVED
            if (onNodeClick) onNodeClick(item || null);
        }

        // Cleanup
        return () => {
            simulation.stop();
        };
    }, [items, onNodeClick]);

    return (
        <div className="constellation-container relative w-full flex-shrink-0 rounded-xl overflow-hidden shadow-inner border border-slate-800" style={{ backgroundColor: "#0f172a", height: "350px" }}>
            {/* Background Stars */}
            <div className="absolute inset-0 opacity-30 pointer-events-none" style={{ backgroundImage: "radial-gradient(white 1px, transparent 1px)", backgroundSize: "50px 50px" }}></div>

            <svg ref={svgRef} className="w-full h-full" width="100%" height="100%" />
        </div>
    );
}
