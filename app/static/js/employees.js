document.addEventListener("DOMContentLoaded", () => {
    if (window.lucide) {
        window.lucide.createIcons();
    }

    document.querySelectorAll("[data-confirm-delete]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (!window.confirm("Удалить сотрудника?")) {
                event.preventDefault();
            }
        });
    });

    const preview = document.getElementById("photo-preview");
    if (preview) {
        const previewImage = preview.querySelector("img");
        const movePreview = (event) => {
            const gap = 18;
            const size = 160;
            const left = Math.min(event.clientX + gap, window.innerWidth - size - gap);
            const top = Math.min(event.clientY + gap, window.innerHeight - size - gap);
            preview.style.left = `${Math.max(gap, left)}px`;
            preview.style.top = `${Math.max(gap, top)}px`;
        };

        document.querySelectorAll("[data-photo-preview]").forEach((image) => {
            image.addEventListener("mouseenter", (event) => {
                previewImage.src = image.src;
                preview.classList.remove("hidden");
                movePreview(event);
            });
            image.addEventListener("mousemove", movePreview);
            image.addEventListener("mouseleave", () => {
                preview.classList.add("hidden");
                previewImage.src = "";
            });
        });
    }

    const photoInput = document.querySelector("[data-photo-input]");
    if (photoInput) {
        const target = document.querySelector("[data-photo-target]");
        const emptyState = document.querySelector("[data-photo-empty]");
        const fileName = document.querySelector("[data-photo-file-name]");
        photoInput.addEventListener("change", () => {
            const file = photoInput.files && photoInput.files[0];
            if (fileName) {
                fileName.textContent = file ? file.name : "Файл не выбран";
            }
            if (!file || !target) {
                return;
            }
            target.src = URL.createObjectURL(file);
            target.classList.remove("hidden");
            if (emptyState) {
                emptyState.classList.add("hidden");
            }
        });
    }
});
