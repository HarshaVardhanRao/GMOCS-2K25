// particlesJS config
particlesJS("particles-js", {
	particles: {
		number: {
			value: 100,
			density: { enable: true, value_area: 800 },
		},
		color: { value: "#a76dff" },
		shape: { type: "circle" },
		opacity: {
			value: 0.6,
			random: true,
			anim: { enable: true, speed: 1, opacity_min: 0.1, sync: false },
		},
		size: {
			value: 3,
			random: true,
			anim: { enable: true, speed: 2, size_min: 0.1, sync: false },
		},
		line_linked: {
			enable: true,
			distance: 150,
			color: "#ff89e9",
			opacity: 0.4,
			width: 1,
		},
		move: {
			enable: true,
			speed: 2,
			direction: "none",
			random: false,
			straight: false,
			out_mode: "out",
			bounce: false,
			attract: { enable: true, rotateX: 600, rotateY: 1200 },
		},
	},
	interactivity: {
		detect_on: "canvas",
		events: {
			onhover: { enable: true, mode: "repulse" },
			onclick: { enable: true, mode: "push" },
			resize: true,
		},
		modes: {
			repulse: { distance: 100, duration: 0.4 },
			push: { particles_nb: 4 },
		},
	},
	retina_detect: true,
});

// Sponsor data
const sponsors = [
	{
		name: "Arva Management Services",
		role: "Exclusive Sponsor",
		image: "/static/img/arva.jpg",
		website: "",
	},
	{
		name: "Hasini Boys PG",
		role: "Sponsor",
		image: "/static/img/image.png",
		website: "",
	},
];

// Function to create sponsor card
function createSponsorCard(sponsor) {
	const imageSrc =
		sponsor.image && sponsor.image.trim() !== "#"
			? sponsor.image
			: "https://photosbull.com/wp-content/uploads/2024/05/no-dp_16.webp";
	return `
      <div class="sponsor-card">
          <div class="sponsor-image-container">
              <img src="${imageSrc}" alt="${
		sponsor.name
	}" class="sponsor-image">
          </div>
          <h2 class="sponsor-name">${sponsor.name}</h2>
          <p class="sponsor-role"><i class="fas fa-handshake"></i> ${
				sponsor.role
			}</p>
          ${
				sponsor.website
					? `<a href="${sponsor.website}" class="sponsor-link" target="_blank">Visit Website</a>`
					: ""
			}
      </div>
  `;
}

// Render sponsors
function renderSponsors() {
	const sponsorContainer = document.getElementById("sponsers-list");
	sponsorContainer.innerHTML = sponsors.map(createSponsorCard).join("");
}

document.addEventListener("DOMContentLoaded", renderSponsors);
