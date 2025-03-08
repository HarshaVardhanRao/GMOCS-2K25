    // Add parallax effect to title and content
document.addEventListener("mousemove", (e) => {
	const contentWrapper = document.querySelector(".content-wrapper");
	const xAxis = (window.innerWidth / 2 - e.pageX) / 25;
	const yAxis = (window.innerHeight / 2 - e.pageY) / 25;

	// Smooth transition for parallax effect
	contentWrapper.style.transform = `
    perspective(1000px)
    rotateY(${xAxis}deg)
    rotateX(${yAxis}deg)
    translateZ(50px)
  `;
});

// Create floating particles
const particlesContainer = document.getElementById("particles");
const numberOfParticles = 50;

for (let i = 0; i < numberOfParticles; i++) {
	const particle = document.createElement("div");
	particle.className = "particle";

	// Random initial position
	particle.style.left = `${Math.random() * 100}%`;

	// Random animation delay
	particle.style.animationDelay = `${Math.random() * 10}s`;

	particlesContainer.appendChild(particle);
}