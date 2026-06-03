// Import bootstrap library
const bootstrap = window.bootstrap

document.addEventListener("DOMContentLoaded", () => {
  const alerts = document.querySelectorAll(".alert")
  alerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert)
      bsAlert.close()
    }, 5000)
  })
})

function updateRatingPreview(value) {
  const stars = document.querySelectorAll(".star-rating i")
  stars.forEach((star, index) => {
    if (index < value) {
      star.classList.remove("far")
      star.classList.add("fas")
    } else {
      star.classList.add("far")
      star.classList.remove("fas")
    }
  })
}

function validateForm(formId) {
  const form = document.getElementById(formId)
  if (form) {
    form.addEventListener("submit", (e) => {
      if (!form.checkValidity()) {
        e.preventDefault()
        e.stopPropagation()
      }
      form.classList.add("was-validated")
    })
  }
}

function filterServices() {
  const searchInput = document.getElementById("serviceSearch")
  if (searchInput) {
    searchInput.addEventListener("keyup", function () {
      const filter = this.value.toLowerCase()
      const services = document.querySelectorAll(".service-card")
      services.forEach((service) => {
        const title = service.querySelector(".card-title").textContent.toLowerCase()
        if (title.includes(filter)) {
          service.style.display = ""
        } else {
          service.style.display = "none"
        }
      })
    })
  }
}

window.addEventListener("load", () => {
  filterServices()
})

document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault()
    const target = document.querySelector(this.getAttribute("href"))
    if (target) {
      target.scrollIntoView({ behavior: "smooth" })
    }
  })
})
