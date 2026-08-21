(() => {
  "use strict";

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const saveData = Boolean(navigator.connection && navigator.connection.saveData);

  const galleries = new Map();

  document.querySelectorAll("[data-gallery]").forEach((track) => {
    const name = track.dataset.gallery;
    const cards = [...track.querySelectorAll(".gallery-card")];
    const output = document.querySelector(`[data-gallery-position="${name}"]`);
    const toggle = document.querySelector(`[data-gallery-autoplay="${name}"]`);
    const canAutoAdvance = track.dataset.autoAdvance === "true" && !reducedMotion.matches && !saveData;
    let userPaused = !canAutoAdvance;
    let isVisible = false;
    let timer = 0;

    const nearestIndex = () => {
      if (!cards.length) return 0;
      const trackMid = track.scrollLeft + track.clientWidth / 2;
      let best = 0;
      let distance = Infinity;
      cards.forEach((card, index) => {
        const cardMid = card.offsetLeft + card.clientWidth / 2;
        const candidate = Math.abs(cardMid - trackMid);
        if (candidate < distance) {
          distance = candidate;
          best = index;
        }
      });
      return best;
    };

    const updatePosition = () => {
      if (output) output.textContent = `${nearestIndex() + 1} of ${cards.length}`;
    };

    const goTo = (index, behavior = "smooth") => {
      if (!cards.length) return;
      const normalized = (index + cards.length) % cards.length;
      cards[normalized].scrollIntoView({ behavior: reducedMotion.matches ? "auto" : behavior, block: "nearest", inline: "center" });
    };

    const stopTimer = () => {
      if (timer) window.clearInterval(timer);
      timer = 0;
    };

    const syncToggle = () => {
      if (!toggle) return;
      toggle.hidden = !canAutoAdvance;
      toggle.setAttribute("aria-pressed", String(!userPaused));
      toggle.textContent = userPaused ? "Resume auto-scroll" : "Pause auto-scroll";
    };

    const startTimer = () => {
      stopTimer();
      if (!canAutoAdvance || userPaused || !isVisible || document.hidden) return;
      timer = window.setInterval(() => goTo(nearestIndex() + 1), 4400);
    };

    track.addEventListener("scroll", () => window.requestAnimationFrame(updatePosition), { passive: true });
    track.addEventListener("pointerdown", stopTimer, { passive: true });
    track.addEventListener("pointerup", startTimer, { passive: true });
    track.addEventListener("focusin", stopTimer);
    track.addEventListener("focusout", startTimer);

    if (toggle) {
      toggle.addEventListener("click", () => {
        userPaused = !userPaused;
        syncToggle();
        startTimer();
      });
    }

    const visibility = new IntersectionObserver((entries) => {
      isVisible = entries[0]?.isIntersecting ?? false;
      startTimer();
    }, { threshold: 0.45 });
    visibility.observe(track);

    galleries.set(name, { goTo, nearestIndex, cards });
    updatePosition();
    syncToggle();
  });

  document.querySelectorAll("[data-gallery-previous]").forEach((button) => {
    button.addEventListener("click", () => {
      const gallery = galleries.get(button.dataset.galleryPrevious);
      if (gallery) gallery.goTo(gallery.nearestIndex() - 1);
    });
  });

  document.querySelectorAll("[data-gallery-next]").forEach((button) => {
    button.addEventListener("click", () => {
      const gallery = galleries.get(button.dataset.galleryNext);
      if (gallery) gallery.goTo(gallery.nearestIndex() + 1);
    });
  });

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      document.querySelectorAll("video[data-play-when-visible]").forEach((video) => video.pause());
    }
  });

  document.querySelectorAll("video[data-play-when-visible]").forEach((video) => {
    let internalPause = false;
    let recentUserInteraction = false;
    let interactionTimer = 0;

    const markUserInteraction = () => {
      recentUserInteraction = true;
      if (interactionTimer) window.clearTimeout(interactionTimer);
      interactionTimer = window.setTimeout(() => {
        recentUserInteraction = false;
      }, 1500);
    };

    video.addEventListener("pointerdown", markUserInteraction);
    video.addEventListener("keydown", markUserInteraction);

    video.addEventListener("pause", () => {
      if (!internalPause && recentUserInteraction && video.currentTime > 0 && !video.ended) {
        video.dataset.userPaused = "true";
      }
      internalPause = false;
    });

    video.addEventListener("play", () => {
      if (recentUserInteraction) delete video.dataset.userPaused;
    });

    if (reducedMotion.matches || saveData) return;

    const observer = new IntersectionObserver((entries) => {
      const entry = entries[0];
      if (entry?.isIntersecting && entry.intersectionRatio >= 0.58 && !video.dataset.userPaused && !document.hidden) {
        video.muted = true;
        video.play().catch(() => {});
      } else if (!video.paused) {
        internalPause = true;
        video.pause();
      }
    }, { threshold: [0, 0.58, 0.9] });

    observer.observe(video);
  });
})();
