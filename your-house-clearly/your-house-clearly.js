(() => {
  "use strict";

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  function setupGallery(gallery) {
    const name = gallery.dataset.gallery;
    const items = Array.from(gallery.children);
    const previous = document.querySelector(`[data-gallery-previous="${name}"]`);
    const next = document.querySelector(`[data-gallery-next="${name}"]`);
    const position = document.querySelector(`[data-gallery-position="${name}"]`);
    const viewport = document.querySelector(`[data-gallery-viewport="${name}"]`);
    const autoplayButton = document.querySelector(`[data-gallery-autoplay="${name}"]`);
    const hint = document.getElementById(gallery.getAttribute("aria-describedby"));
    const supportsAutoplay = gallery.dataset.autoAdvance === "true";
    let currentIndex = 0;
    let autoplayPaused = reducedMotion.matches;
    let isVisible = false;
    let timer = null;
    let scrollUpdate = null;

    if (!items.length || !previous || !next || !position || !viewport) return;

    items.forEach((item, index) => {
      item.setAttribute("role", "group");
      item.setAttribute("aria-roledescription", "slide");
      item.setAttribute("aria-label", `${index + 1} of ${items.length}`);
    });

    function nearestIndex() {
      const galleryLeft = gallery.getBoundingClientRect().left;
      let nearest = 0;
      let distance = Number.POSITIVE_INFINITY;
      items.forEach((item, index) => {
        const itemDistance = Math.abs(item.getBoundingClientRect().left - galleryLeft);
        if (itemDistance < distance) {
          distance = itemDistance;
          nearest = index;
        }
      });
      return nearest;
    }

    function updateState() {
      currentIndex = nearestIndex();
      position.value = `${currentIndex + 1} of ${items.length}`;
      position.textContent = position.value;
      previous.disabled = currentIndex === 0;
      next.disabled = currentIndex === items.length - 1;
      viewport.dataset.atStart = String(gallery.scrollLeft <= 2);
      viewport.dataset.atEnd = String(
        gallery.scrollLeft + gallery.clientWidth >= gallery.scrollWidth - 2
      );
    }

    function goTo(index, behavior = reducedMotion.matches ? "auto" : "smooth") {
      const boundedIndex = Math.max(0, Math.min(items.length - 1, index));
      items[boundedIndex].scrollIntoView({ behavior, block: "nearest", inline: "start" });
      currentIndex = boundedIndex;
      window.setTimeout(updateState, behavior === "smooth" ? 450 : 0);
    }

    function stopTimer() {
      if (timer !== null) {
        window.clearInterval(timer);
        timer = null;
      }
    }

    function startTimer() {
      stopTimer();
      if (!supportsAutoplay || autoplayPaused || !isVisible || reducedMotion.matches) return;
      timer = window.setInterval(() => {
        const nextIndex = currentIndex >= items.length - 1 ? 0 : currentIndex + 1;
        goTo(nextIndex);
      }, 6000);
    }

    function setAutoplayPaused(paused) {
      autoplayPaused = paused;
      if (autoplayButton) {
        autoplayButton.hidden = reducedMotion.matches;
        autoplayButton.setAttribute("aria-pressed", String(!paused));
        autoplayButton.textContent = paused ? "Resume auto-scroll" : "Pause auto-scroll";
      }
      position.setAttribute("aria-live", paused ? "polite" : "off");
      if (supportsAutoplay && hint) {
        hint.textContent = reducedMotion.matches
          ? "Automatic movement is off for your motion setting. Swipe or use the buttons to see all eight screens."
          : "The gallery advances while it is in view. Swipe or use the buttons at any time.";
      }
      startTimer();
    }

    function pauseAfterInteraction() {
      if (supportsAutoplay && !autoplayPaused) setAutoplayPaused(true);
    }

    previous.addEventListener("click", () => {
      pauseAfterInteraction();
      goTo(currentIndex - 1);
    });
    next.addEventListener("click", () => {
      pauseAfterInteraction();
      goTo(currentIndex + 1);
    });
    autoplayButton?.addEventListener("click", () => setAutoplayPaused(!autoplayPaused));

    gallery.addEventListener("scroll", () => {
      window.cancelAnimationFrame(scrollUpdate);
      scrollUpdate = window.requestAnimationFrame(updateState);
    }, { passive: true });
    gallery.addEventListener("pointerdown", pauseAfterInteraction, { passive: true });
    gallery.addEventListener("wheel", pauseAfterInteraction, { passive: true });
    gallery.addEventListener("keydown", (event) => {
      let target = null;
      if (event.key === "ArrowLeft") target = currentIndex - 1;
      if (event.key === "ArrowRight") target = currentIndex + 1;
      if (event.key === "Home") target = 0;
      if (event.key === "End") target = items.length - 1;
      if (target === null) return;
      event.preventDefault();
      pauseAfterInteraction();
      goTo(target);
    });

    const visibilityObserver = new IntersectionObserver((entries) => {
      isVisible = entries[0]?.isIntersecting ?? false;
      startTimer();
    }, { threshold: 0.15 });
    visibilityObserver.observe(gallery);

    const motionListener = () => setAutoplayPaused(reducedMotion.matches || autoplayPaused);
    reducedMotion.addEventListener?.("change", motionListener);

    setAutoplayPaused(autoplayPaused);
    updateState();
  }

  document.querySelectorAll("[data-gallery]").forEach(setupGallery);

  const video = document.querySelector("[data-play-when-visible]");
  if (video) {
    video.defaultMuted = true;
    const saveData = navigator.connection?.saveData === true;
    const playbackNote = document.getElementById("tour-playback-note");
    let autoplayAllowed = !reducedMotion.matches && !saveData;
    if (!autoplayAllowed && playbackNote) {
      playbackNote.textContent = "Automatic playback is off for your browser settings. Use the video controls to play.";
    }
    const markUserControlled = () => { autoplayAllowed = false; };
    video.addEventListener("pointerdown", markUserControlled, { passive: true });
    video.addEventListener("keydown", markUserControlled);
    video.addEventListener("volumechange", () => {
      if (!video.muted) autoplayAllowed = false;
    });
    if (!reducedMotion.matches && !saveData) {
      const videoObserver = new IntersectionObserver((entries) => {
        const entry = entries[0];
        if (autoplayAllowed && entry?.isIntersecting && entry.intersectionRatio >= 0.6) {
          video.play().catch(() => {});
        } else {
          video.pause();
        }
      }, { threshold: [0, 0.6] });
      videoObserver.observe(video);
      reducedMotion.addEventListener?.("change", () => {
        if (reducedMotion.matches) {
          autoplayAllowed = false;
          video.pause();
          if (playbackNote) {
            playbackNote.textContent = "Automatic playback is off for your motion setting. Use the video controls to play.";
          }
        }
      });
    }
  }
})();
