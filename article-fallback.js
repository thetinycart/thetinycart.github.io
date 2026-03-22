document.addEventListener("DOMContentLoaded", () => {
  const heroImage = document.querySelector("article > img");
  const heroSrc = heroImage ? heroImage.getAttribute("src") : "";

  const cleanLabel = (label) =>
    (label || "Product")
      .replace(/^\d+\.\s*/, "")
      .replace(/\s+/g, " ")
      .trim();

  const makeMonogram = (label) => {
    const words = cleanLabel(label)
      .split(" ")
      .filter(Boolean)
      .slice(0, 2);
    return words.map((word) => word[0].toUpperCase()).join("") || "TC";
  };

  const buildPlaceholderFrame = (label) => {
    const frame = document.createElement("div");
    frame.className = "product-img product-img--placeholder";

    const placeholder = document.createElement("div");
    placeholder.className = "product-placeholder";
    if (heroSrc && heroSrc.startsWith("/")) {
      placeholder.style.setProperty("--placeholder-image", `url("${heroSrc}")`);
    }

    const monogram = document.createElement("span");
    monogram.className = "product-placeholder-monogram";
    monogram.textContent = makeMonogram(label);

    const badge = document.createElement("span");
    badge.className = "product-placeholder-badge";
    badge.textContent = "Product preview";

    const title = document.createElement("strong");
    title.textContent = cleanLabel(label);

    const note = document.createElement("p");
    note.textContent = "Open Amazon for the latest photo, color options, price, and availability.";

    placeholder.append(monogram, badge, title, note);
    frame.appendChild(placeholder);
    return frame;
  };

  const ensurePlaceholder = (box, label) => {
    const existingFrame = box.querySelector(".product-img");
    const placeholderFrame = buildPlaceholderFrame(label);

    if (existingFrame) {
      existingFrame.replaceWith(placeholderFrame);
    } else {
      const info = box.querySelector(".product-info");
      if (info) {
        box.insertBefore(placeholderFrame, info);
      } else {
        box.prepend(placeholderFrame);
      }
    }

    box.classList.add("no-product-image");
  };

  const labelForBox = (box, imageAlt) =>
    imageAlt || box.querySelector(".product-info h3")?.textContent || box.querySelector("h3")?.textContent || "Product";

  document.querySelectorAll(".product-box").forEach((box) => {
    const img = box.querySelector(".product-img img");
    const label = labelForBox(box, img?.alt);

    if (!img) {
      ensurePlaceholder(box, label);
      return;
    }

    const replaceBrokenImage = () => {
      ensurePlaceholder(box, labelForBox(box, img.alt));
    };

    img.addEventListener("error", replaceBrokenImage, { once: true });

    if (img.complete && img.naturalWidth === 0) {
      replaceBrokenImage();
    }
  });
});
