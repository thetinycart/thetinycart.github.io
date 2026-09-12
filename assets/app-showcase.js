(() => {
  "use strict";

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const saveData = Boolean(navigator.connection && navigator.connection.saveData);
  const galleries = new Map();
  const videos = [];

  document.querySelectorAll("[data-gallery]").forEach((track) => {
    const name = track.dataset.gallery;
    const cards = [...track.children];
    const viewport = document.querySelector(`[data-gallery-viewport="${name}"]`);
    const output = document.querySelector(`[data-gallery-position="${name}"]`);
    const toggle = document.querySelector(`[data-gallery-autoplay="${name}"]`);
    const previous = document.querySelector(`[data-gallery-previous="${name}"]`);
    const next = document.querySelector(`[data-gallery-next="${name}"]`);
    const trackID = track.id || `${name}-gallery`;
    let currentIndex = 0;
    let userPaused = track.dataset.autoAdvance !== "true" || reducedMotion.matches || saveData;
    let isVisible = false;
    let timer = 0;
    let scrollFrame = 0;

    track.id = trackID;
    cards.forEach((card, index) => {
      card.setAttribute("role", "group");
      card.setAttribute("aria-roledescription", "slide");
      card.setAttribute("aria-label", `${index + 1} of ${cards.length}`);
    });
    [previous, next, toggle].forEach((control) => {
      if (control) control.setAttribute("aria-controls", trackID);
    });

    const hasOverflow = () => track.scrollWidth > track.clientWidth + 1;
    const canAutoAdvance = () => (
      hasOverflow() && track.dataset.autoAdvance === "true" && !reducedMotion.matches && !saveData
    );

    const nearestIndex = () => {
      if (!cards.length) return 0;
      // A nearly full-width row cannot center its edge cards. Use the real
      // scroll boundaries so an arrow never promises movement past an edge.
      if (track.scrollLeft <= 1) return 0;
      if (track.scrollLeft >= track.scrollWidth - track.clientWidth - 1) return cards.length - 1;
      const trackMid = track.getBoundingClientRect().left + track.clientWidth / 2;
      let best = 0;
      let distance = Number.POSITIVE_INFINITY;
      cards.forEach((card, index) => {
        const cardMid = card.getBoundingClientRect().left + card.clientWidth / 2;
        const candidate = Math.abs(cardMid - trackMid);
        if (candidate < distance) {
          distance = candidate;
          best = index;
        }
      });
      return best;
    };

    const updateState = () => {
      const scrollable = hasOverflow();
      currentIndex = nearestIndex();
      if (output) {
        const value = scrollable ? `${currentIndex + 1} of ${cards.length}` : `All ${cards.length} shown`;
        output.value = value;
        output.textContent = value;
        output.setAttribute("aria-live", canAutoAdvance() && !userPaused ? "off" : "polite");
        output.setAttribute("aria-atomic", "true");
      }
      if (previous) {
        previous.hidden = !scrollable;
        previous.disabled = !scrollable || currentIndex === 0;
      }
      if (next) {
        next.hidden = !scrollable;
        next.disabled = !scrollable || currentIndex === cards.length - 1;
      }
      if (viewport) {
        viewport.dataset.atStart = String(track.scrollLeft <= 2);
        viewport.dataset.atEnd = String(track.scrollLeft + track.clientWidth >= track.scrollWidth - 2);
      }
    };

    const goTo = (index, { behavior = "smooth", wrap = false } = {}) => {
      if (!cards.length || !hasOverflow()) return;
      const target = wrap
        ? (index + cards.length) % cards.length
        : Math.max(0, Math.min(cards.length - 1, index));
      const targetLeft = cards[target].getBoundingClientRect().left
        - track.getBoundingClientRect().left + track.scrollLeft
        + (cards[target].clientWidth - track.clientWidth) / 2;
      // Move only the gallery. scrollIntoView also shifts the page vertically,
      // which can hide its navigation controls beneath the sticky header.
      track.scrollTo({
        left: Math.max(0, Math.min(track.scrollWidth - track.clientWidth, targetLeft)),
        behavior: reducedMotion.matches ? "auto" : behavior,
      });
      currentIndex = target;
      window.setTimeout(updateState, behavior === "smooth" && !reducedMotion.matches ? 450 : 0);
    };

    const stopTimer = () => {
      if (timer) window.clearInterval(timer);
      timer = 0;
    };

    const syncToggle = () => {
      if (toggle) {
        toggle.hidden = !canAutoAdvance();
        toggle.setAttribute("aria-pressed", String(!userPaused));
        toggle.textContent = userPaused ? "Resume auto-scroll" : "Pause auto-scroll";
      }
      if (output) output.setAttribute("aria-live", canAutoAdvance() && !userPaused ? "off" : "polite");
    };

    const startTimer = () => {
      stopTimer();
      if (!canAutoAdvance() || userPaused || !isVisible || document.hidden) return;
      timer = window.setInterval(() => {
        const target = currentIndex >= cards.length - 1 ? 0 : currentIndex + 1;
        goTo(target, { wrap: true });
      }, 4400);
    };

    const setUserPaused = (paused) => {
      userPaused = paused;
      syncToggle();
      startTimer();
    };

    const pauseAfterInteraction = () => {
      if (canAutoAdvance() && !userPaused) {
        setUserPaused(true);
      } else {
        stopTimer();
      }
    };

    let togglePointerTargetPaused = null;

    track.addEventListener("scroll", () => {
      window.cancelAnimationFrame(scrollFrame);
      scrollFrame = window.requestAnimationFrame(updateState);
    }, { passive: true });
    track.addEventListener("pointerdown", pauseAfterInteraction, { passive: true });
    track.addEventListener("wheel", pauseAfterInteraction, { passive: true });
    track.addEventListener("focusin", pauseAfterInteraction);
    track.addEventListener("keydown", (event) => {
      if (!hasOverflow()) return;
      let target = null;
      if (event.key === "ArrowLeft") target = currentIndex - 1;
      if (event.key === "ArrowRight") target = currentIndex + 1;
      if (event.key === "Home") target = 0;
      if (event.key === "End") target = cards.length - 1;
      if (target === null) return;
      event.preventDefault();
      pauseAfterInteraction();
      goTo(target);
    });

    previous?.addEventListener("click", () => {
      pauseAfterInteraction();
      goTo(currentIndex - 1);
    });
    next?.addEventListener("click", () => {
      pauseAfterInteraction();
      goTo(currentIndex + 1);
    });
    previous?.addEventListener("focusin", pauseAfterInteraction);
    next?.addEventListener("focusin", pauseAfterInteraction);
    toggle?.addEventListener("pointerdown", () => {
      // Pointer activation moves focus before `click`. Preserve the meaning of
      // the label the pointer user chose instead of treating that focus move as
      // a separate keyboard pause.
      togglePointerTargetPaused = !userPaused;
    }, { passive: true });
    toggle?.addEventListener("pointercancel", () => {
      togglePointerTargetPaused = null;
    }, { passive: true });
    toggle?.addEventListener("pointerup", () => {
      const pendingTarget = togglePointerTargetPaused;
      window.setTimeout(() => {
        if (togglePointerTargetPaused === pendingTarget) {
          togglePointerTargetPaused = null;
        }
      }, 0);
    }, { passive: true });
    toggle?.addEventListener("focusin", () => {
      if (togglePointerTargetPaused === null) pauseAfterInteraction();
    });
    toggle?.addEventListener("click", () => {
      const targetPaused = togglePointerTargetPaused;
      togglePointerTargetPaused = null;
      setUserPaused(targetPaused === null ? !userPaused : targetPaused);
    });

    const visibility = new IntersectionObserver((entries) => {
      isVisible = entries[0]?.isIntersecting ?? false;
      startTimer();
    }, { threshold: 0.45 });
    visibility.observe(track);

    const refresh = () => {
      if (reducedMotion.matches && !userPaused) userPaused = true;
      syncToggle();
      updateState();
      startTimer();
    };

    galleries.set(name, { refresh });
    new ResizeObserver(refresh).observe(track);
    refresh();
  });

  document.querySelectorAll("video[data-play-when-visible]").forEach((video) => {
    let isVisible = false;
    let isOnScreen = false;
    let userControlled = false;
    let managedPlaybackIntent = null;

    video.defaultMuted = true;

    const autoplayAllowed = () => !reducedMotion.matches && !saveData;
    const markUserControlled = () => { userControlled = true; };
    const pause = () => {
      if (!video.paused) {
        managedPlaybackIntent = "pause";
        video.pause();
      }
    };
    const play = () => {
      if (!video.paused) return;
      managedPlaybackIntent = "play";
      video.play().catch(() => {
        if (managedPlaybackIntent === "play") managedPlaybackIntent = null;
      });
    };
    const syncPlayback = () => {
      if (document.hidden) {
        pause();
        return;
      }
      // Reduced motion and Save-Data suppress automatic playback, not a
      // person's deliberate Play action. Keep that intent while partially
      // visible, and do not automatically resume after they pause.
      if (userControlled) {
        if (!isOnScreen) pause();
        return;
      }
      if (!isVisible || !autoplayAllowed()) {
        pause();
        return;
      }
      video.muted = true;
      play();
    };

    video.addEventListener("pointerdown", markUserControlled, { passive: true });
    video.addEventListener("keydown", markUserControlled);
    video.addEventListener("volumechange", () => {
      if (!video.muted) userControlled = true;
    });
    video.addEventListener("pause", () => {
      if (managedPlaybackIntent === "pause") {
        managedPlaybackIntent = null;
      } else {
        userControlled = true;
      }
    });
    video.addEventListener("play", () => {
      if (managedPlaybackIntent === "play") {
        managedPlaybackIntent = null;
      } else {
        userControlled = true;
      }
    });

    const observer = new IntersectionObserver((entries) => {
      const entry = entries[0];
      isOnScreen = Boolean(entry?.isIntersecting);
      isVisible = Boolean(entry?.isIntersecting && entry.intersectionRatio >= 0.58);
      syncPlayback();
    }, { threshold: [0, 0.58, 0.9] });

    observer.observe(video);
    videos.push({ syncPlayback });
  });

  document.addEventListener("visibilitychange", () => {
    galleries.forEach(({ refresh }) => refresh());
    videos.forEach(({ syncPlayback }) => syncPlayback());
  });

  reducedMotion.addEventListener?.("change", () => {
    galleries.forEach(({ refresh }) => refresh());
    videos.forEach(({ syncPlayback }) => syncPlayback());
  });
})();
