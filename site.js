(() => {
  const groups = [...document.querySelectorAll(".card-shots, .shots")]
    .map((container) => ({
      container,
      images: [...container.querySelectorAll("img")],
    }))
    .filter((group) => group.images.length);

  if (!groups.length) return;

  const lightbox = document.createElement("div");
  lightbox.className = "lightbox";
  lightbox.hidden = true;
  lightbox.setAttribute("role", "dialog");
  lightbox.setAttribute("aria-modal", "true");
  lightbox.setAttribute("aria-label", "Game screenshots");
  lightbox.innerHTML = `
    <button class="lightbox-close" type="button" aria-label="Close screenshot gallery">×</button>
    <button class="lightbox-nav lightbox-prev" type="button" aria-label="Previous screenshot">‹</button>
    <figure class="lightbox-figure">
      <img class="lightbox-image" alt="">
      <figcaption class="lightbox-count" aria-live="polite"></figcaption>
    </figure>
    <button class="lightbox-nav lightbox-next" type="button" aria-label="Next screenshot">›</button>`;
  document.body.appendChild(lightbox);

  const fullImage = lightbox.querySelector(".lightbox-image");
  const count = lightbox.querySelector(".lightbox-count");
  const closeButton = lightbox.querySelector(".lightbox-close");
  const prevButton = lightbox.querySelector(".lightbox-prev");
  const nextButton = lightbox.querySelector(".lightbox-next");
  let activeImages = [];
  let activeIndex = 0;
  let returnFocus = null;

  const render = () => {
    const source = activeImages[activeIndex];
    fullImage.src = source.currentSrc || source.src;
    fullImage.alt = source.alt || "Game screenshot";
    count.textContent = `${activeIndex + 1} / ${activeImages.length}`;
    const multiple = activeImages.length > 1;
    prevButton.hidden = !multiple;
    nextButton.hidden = !multiple;
  };

  const move = (direction) => {
    activeIndex = (activeIndex + direction + activeImages.length) % activeImages.length;
    render();
  };

  const open = (images, index, trigger) => {
    activeImages = images;
    activeIndex = index;
    returnFocus = trigger;
    render();
    lightbox.hidden = false;
    document.body.classList.add("lightbox-open");
    closeButton.focus();
  };

  const close = () => {
    if (lightbox.hidden) return;
    lightbox.hidden = true;
    document.body.classList.remove("lightbox-open");
    fullImage.removeAttribute("src");
    returnFocus?.focus();
  };

  groups.forEach(({ container, images }) => {
    container.setAttribute("aria-label", "Open screenshot gallery");
    images.forEach((image, index) => {
      image.tabIndex = 0;
      image.setAttribute("role", "button");
      image.setAttribute("aria-label", `Open screenshot ${index + 1} of ${images.length}`);
      image.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        open(images, index, image);
      });
      image.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          event.stopPropagation();
          open(images, index, image);
        }
      });
    });
  });

  closeButton.addEventListener("click", close);
  prevButton.addEventListener("click", () => move(-1));
  nextButton.addEventListener("click", () => move(1));
  fullImage.addEventListener("click", () => {
    if (activeImages.length > 1) move(1);
  });
  lightbox.addEventListener("click", (event) => {
    if (event.target === lightbox) close();
  });
  document.addEventListener("keydown", (event) => {
    if (lightbox.hidden) return;
    if (event.key === "Escape") close();
    if (event.key === "ArrowLeft") move(-1);
    if (event.key === "ArrowRight") move(1);
  });
})();
