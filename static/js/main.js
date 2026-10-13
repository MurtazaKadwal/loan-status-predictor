document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loan-form");
  const button = form?.querySelector(".submit-button");
  if (form && button) {
    form.addEventListener("submit", () => {
      button.disabled = true;
      button.querySelector("span:first-child").textContent = "Generating…";
      button.style.opacity = ".78";
    });
  }

  const editButton = document.getElementById("edit-inputs");
  if (editButton) {
    editButton.addEventListener("click", () => {
      document.getElementById("loan-form")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  // If a prediction is shown, bring the result into view on narrow screens.
  const result = document.getElementById("result");
  if (result && result.querySelector(".result-content") && window.innerWidth < 980) {
    window.setTimeout(() => result.scrollIntoView({ behavior: "smooth", block: "start" }), 120);
  }
});
