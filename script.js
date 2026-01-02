const slides = document.querySelectorAll(".slide");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");

let currentSlide = 0;
const totalSlides = slides.length;
const fragmentProgress = Array.from({ length: totalSlides }, () => 0);
let lastSlide = 0;

function getFragments(slideEl) {
  return Array.from(slideEl.querySelectorAll(".fragment"));
}

function updateSlide() {
  // Optional per-slide behavior: reset fragments on entry (use data-reset-fragments="true")
  if (currentSlide !== lastSlide) {
    const active = slides[currentSlide];
    if (active && active.dataset && active.dataset.resetFragments === "true") {
      fragmentProgress[currentSlide] = 0;
    }
    lastSlide = currentSlide;
  }

  slides.forEach((slide, index) => {
    slide.classList.remove("active", "prev");
    const videos = slide.querySelectorAll("video");

    if (index === currentSlide) {
      slide.classList.add("active");
      // Play videos in active slide
      videos.forEach((v) => {
        v.currentTime = 0;
        v.play().catch((e) => console.error("Video play failed:", e));
      });
    } else if (index < currentSlide) {
      slide.classList.add("prev");
      // Pause videos in inactive slides
      videos.forEach((v) => v.pause());
    } else {
      // Pause videos in future slides
      videos.forEach((v) => v.pause());
    }

    // Reset fragment visibility for all slides, then re-apply for active slide
    const fragments = getFragments(slide);
    fragments.forEach((el) => el.classList.remove("visible"));
    if (index === currentSlide) {
      const shown = fragmentProgress[index] || 0;
      fragments.slice(0, shown).forEach((el) => el.classList.add("visible"));
    }
  });
}

function nextSlide() {
  if (currentSlide < totalSlides - 1) {
    currentSlide++;
    updateSlide();
  }
}

function prevSlide() {
  if (currentSlide > 0) {
    currentSlide--;
    updateSlide();
  }
}

function nextStep() {
  const slide = slides[currentSlide];
  const fragments = getFragments(slide);
  const shown = fragmentProgress[currentSlide] || 0;

  if (shown < fragments.length) {
    fragments[shown].classList.add("visible");
    fragmentProgress[currentSlide] = shown + 1;
    return;
  }

  nextSlide();
}

function prevStep() {
  const slide = slides[currentSlide];
  const fragments = getFragments(slide);
  const shown = fragmentProgress[currentSlide] || 0;

  if (shown > 0) {
    fragmentProgress[currentSlide] = shown - 1;
    fragments[shown - 1].classList.remove("visible");
    return;
  }

  prevSlide();
}

// Event Listeners
prevBtn.addEventListener("click", prevStep);
nextBtn.addEventListener("click", nextStep);

document.addEventListener("keydown", (e) => {
  if (e.key === "ArrowRight" || e.key === " " || e.key === "Enter") {
    e.preventDefault();
    nextStep();
  } else if (e.key === "ArrowLeft" || e.key === "Backspace") {
    e.preventDefault();
    prevStep();
  }
});

let wheelLocked = false;
document.addEventListener(
  "wheel",
  (e) => {
    if (wheelLocked) return;
    wheelLocked = true;
    setTimeout(() => {
      wheelLocked = false;
    }, 250);

    if (e.deltaY > 0) nextStep();
    else if (e.deltaY < 0) prevStep();
  },
  { passive: true }
);

// Initialize
updateSlide();
