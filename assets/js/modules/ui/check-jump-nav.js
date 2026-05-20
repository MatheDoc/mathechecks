const jumpNavEnhancements = new WeakMap();

function getScrollStep(navNode) {
  return Math.max(160, Math.round(navNode.clientWidth * 0.72));
}

function createScrollButton(direction, navNode) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = `check-jump-nav-scroll check-jump-nav-scroll--${direction}`;
  button.dataset.direction = direction;
  button.setAttribute(
    "aria-label",
    direction === "left"
      ? "Check-Navigation nach links scrollen"
      : "Check-Navigation nach rechts scrollen"
  );

  if (navNode.id) {
    button.setAttribute("aria-controls", navNode.id);
  }

  const icon = document.createElement("span");
  icon.setAttribute("aria-hidden", "true");
  icon.textContent = direction === "left" ? "\u00AB" : "\u00BB";
  button.appendChild(icon);
  return button;
}

export function enhanceCheckJumpNav(navNode) {
  if (!navNode) return;

  const wrap = navNode.closest(".check-jump-nav-wrap");
  if (!wrap) return;

  let state = jumpNavEnhancements.get(navNode);

  if (!state) {
    const leftButton = wrap.querySelector(".check-jump-nav-scroll--left") || createScrollButton("left", navNode);
    const rightButton = wrap.querySelector(".check-jump-nav-scroll--right") || createScrollButton("right", navNode);

    if (!leftButton.isConnected) {
      wrap.insertBefore(leftButton, navNode);
    }
    if (!rightButton.isConnected) {
      wrap.appendChild(rightButton);
    }

    let frameRequested = false;
    const updateButtons = () => {
      const maxScrollLeft = Math.max(0, navNode.scrollWidth - navNode.clientWidth);
      const canScroll = maxScrollLeft > 8;
      const scrollLeft = navNode.scrollLeft;

      wrap.classList.toggle("check-jump-nav-wrap--scrollable", canScroll);
      leftButton.hidden = !canScroll;
      rightButton.hidden = !canScroll;
      leftButton.disabled = !canScroll || scrollLeft <= 4;
      rightButton.disabled = !canScroll || scrollLeft >= maxScrollLeft - 4;
    };

    const requestUpdate = () => {
      if (frameRequested) return;
      frameRequested = true;
      window.requestAnimationFrame(() => {
        frameRequested = false;
        updateButtons();
      });
    };

    const handleButtonClick = (event) => {
      const direction = event.currentTarget.dataset.direction === "left" ? -1 : 1;
      navNode.scrollBy({
        left: direction * getScrollStep(navNode),
        behavior: "smooth",
      });
    };

    let resizeObserver = null;
    if (typeof ResizeObserver === "function") {
      resizeObserver = new ResizeObserver(() => {
        requestUpdate();
      });
      resizeObserver.observe(navNode);
    }

    navNode.addEventListener("scroll", requestUpdate, { passive: true });
    window.addEventListener("resize", requestUpdate);
    leftButton.addEventListener("click", handleButtonClick);
    rightButton.addEventListener("click", handleButtonClick);

    state = {
      leftButton,
      rightButton,
      updateButtons,
      requestUpdate,
      resizeObserver,
    };
    jumpNavEnhancements.set(navNode, state);
  }

  if (navNode.id) {
    state.leftButton.setAttribute("aria-controls", navNode.id);
    state.rightButton.setAttribute("aria-controls", navNode.id);
  }

  state.updateButtons();
  window.requestAnimationFrame(() => {
    state.requestUpdate();
  });
}