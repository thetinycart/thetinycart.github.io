document.addEventListener("DOMContentLoaded", () => {
  const hideBrokenProductImage = (img) => {
    const frame = img.closest(".product-img");
    const box = img.closest(".product-box");
    if (frame) {
      frame.remove();
    }
    if (box) {
      box.classList.add("no-product-image");
    }
  };

  document.querySelectorAll(".product-box .product-img img").forEach((img) => {
    img.addEventListener(
      "error",
      () => {
        hideBrokenProductImage(img);
      },
      { once: true }
    );

    if (img.complete && img.naturalWidth === 0) {
      hideBrokenProductImage(img);
    }
  });
});
