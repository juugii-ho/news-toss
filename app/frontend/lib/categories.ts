// Category icon mapping
export const CATEGORY_ICONS: Record<string, { icon: string; image: string; color: string; bg: string }> = {
    Politics: {
        icon: "🏛️",
        image: "/assets/categories/politics.png",
        color: "#4338ca", // Indigo-700
        bg: "rgba(99, 102, 241, 0.1)"
    },
    Economy: {
        icon: "💰",
        image: "/assets/categories/economy.png",
        color: "#0f766e", // Teal-700
        bg: "rgba(20, 184, 166, 0.1)"
    },
    Society: {
        icon: "👥",
        image: "/assets/categories/society.png",
        color: "#7c3aed", // Violet-600
        bg: "rgba(139, 92, 246, 0.1)"
    },
    Tech: {
        icon: "💻",
        image: "/assets/categories/tech.png",
        color: "#0284c7", // Sky-600
        bg: "rgba(14, 165, 233, 0.1)"
    },
    World: {
        icon: "🌍",
        image: "/assets/categories/world.png",
        color: "#059669", // Emerald-600
        bg: "rgba(16, 185, 129, 0.1)"
    },
    Culture: {
        icon: "🎨",
        image: "/assets/categories/culture.png",
        color: "#db2777", // Pink-600
        bg: "rgba(236, 72, 153, 0.1)"
    },
    Sports: {
        icon: "⚽",
        image: "/assets/categories/sports.png",
        color: "#ea580c", // Orange-600
        bg: "rgba(249, 115, 22, 0.1)"
    },
    Entertainment: {
        icon: "🎬",
        image: "/assets/categories/entertainment.png",
        color: "#dc2626", // Red-600
        bg: "rgba(239, 68, 68, 0.1)"
    },
    Unclassified: {
        icon: "📰",
        image: "/assets/categories/politics.png", // Fallback to politics or generic
        color: "#64748b", // Neutral-500
        bg: "rgba(100, 116, 139, 0.1)"
    }
};

export function getCategoryIcon(category?: string | null) {
    if (!category) return CATEGORY_ICONS.Unclassified;
    return CATEGORY_ICONS[category] || CATEGORY_ICONS.Unclassified;
}
