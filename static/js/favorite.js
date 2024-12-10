document.addEventListener("DOMContentLoaded", function () {
  const favoriteForm = document.querySelector('form[action*="favorite"]');
  if (favoriteForm) {
    favoriteForm.addEventListener("submit", function (e) {
      e.preventDefault();
      fetch(this.action, {
        method: "POST",
        headers: {
          "X-CSRFToken": this.querySelector("[name=csrfmiddlewaretoken]").value,
        },
        credentials: "same-origin",
      })
        .then((response) => response.ok && window.location.reload())
        .catch((error) => console.error("Error:", error));
    });
  }
});
