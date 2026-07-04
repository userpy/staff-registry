(function () {
    const iconPaths = {
        "arrow-left": '<path d="M19 12H5"></path><path d="m12 19-7-7 7-7"></path>',
        "chevron-left": '<path d="m15 18-6-6 6-6"></path>',
        "chevron-right": '<path d="m9 18 6-6-6-6"></path>',
        "pencil": '<path d="M21.2 6.8 17.2 2.8a2.8 2.8 0 0 0-4 0L3 13v5h5L18.2 7.8a2.8 2.8 0 0 0 3 0Z"></path><path d="M12 4 20 12"></path>',
        "plus": '<path d="M12 5v14"></path><path d="M5 12h14"></path>',
        "rotate-ccw": '<path d="M3 2v6h6"></path><path d="M3 13a9 9 0 1 0 3-6.7L3 8"></path>',
        "save": '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2Z"></path><path d="M17 21v-8H7v8"></path><path d="M7 3v5h8"></path>',
        "search": '<circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.3-4.3"></path>',
        "table-2": '<path d="M9 3H5a2 2 0 0 0-2 2v4h6V3Z"></path><path d="M21 9V5a2 2 0 0 0-2-2h-6v6h8Z"></path><path d="M3 13v6a2 2 0 0 0 2 2h4v-8H3Z"></path><path d="M13 21h6a2 2 0 0 0 2-2v-6h-8v8Z"></path>',
        "trash-2": '<path d="M3 6h18"></path><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"></path><path d="M10 11v6"></path><path d="M14 11v6"></path>',
        "user-plus": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M19 8v6"></path><path d="M22 11h-6"></path>',
        "x": '<path d="M18 6 6 18"></path><path d="m6 6 12 12"></path>',
    };

    function createIcons() {
        document.querySelectorAll("[data-lucide]").forEach((element) => {
            const iconName = element.getAttribute("data-lucide");
            const paths = iconPaths[iconName];
            if (!paths) {
                return;
            }

            const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            svg.setAttribute("xmlns", "http://www.w3.org/2000/svg");
            svg.setAttribute("viewBox", "0 0 24 24");
            svg.setAttribute("fill", "none");
            svg.setAttribute("stroke", "currentColor");
            svg.setAttribute("stroke-width", "2");
            svg.setAttribute("stroke-linecap", "round");
            svg.setAttribute("stroke-linejoin", "round");
            svg.setAttribute("aria-hidden", "true");

            const className = element.getAttribute("class");
            if (className) {
                svg.setAttribute("class", className);
            }

            svg.innerHTML = paths;
            element.replaceWith(svg);
        });
    }

    window.lucide = { createIcons };
})();
