particlesJS('particles-js', {
    particles: {
      number: {
        value: 100,
        density: {
          enable: true,
          value_area: 800
        }
      },
      color: {
        value: '#a76dff'
      },
      shape: {
        type: 'circle'
      },
      opacity: {
        value: 0.6,
        random: true,
        anim: {
          enable: true,
          speed: 1,
          opacity_min: 0.1,
          sync: false
        }
      },
      size: {
        value: 3,
        random: true,
        anim: {
          enable: true,
          speed: 2,
          size_min: 0.1,
          sync: false
        }
      },
      line_linked: {
        enable: true,
        distance: 150,
        color: '#ff89e9',
        opacity: 0.4,
        width: 1
      },
      move: {
        enable: true,
        speed: 2,
        direction: 'none',
        random: false,
        straight: false,
        out_mode: 'out',
        bounce: false,
        attract: {
          enable: true,
          rotateX: 600,
          rotateY: 1200
        }
      }
    },
    interactivity: {
      detect_on: 'canvas',
      events: {
        onhover: {
          enable: true,
          mode: 'repulse'
        },
        onclick: {
          enable: true,
          mode: 'push'
        },
        resize: true
      },
      modes: {
        repulse: {
          distance: 100,
          duration: 0.4
        },
        push: {
          particles_nb: 4
        }
      }
    },
    retina_detect: true
  });

// Faculty committee data
const facultyCommittee = [
    {
        name: "",
        role: "Faculty Co-Ordinator",
        image: "static/img/GMOCSLogo.png",
        linkedin: "https://www.linkedin.com/",
        phone: "",
        email: ""
    },
    {
        name: "",
        role: "Faculty Co-Ordinator",
        image: "#",
        linkedin: "https://www.linkedin.com/",
        phone: "",
        email: ""
    }
];

// Student committee data
const studentCommittee = [
    {
        name: "",
        role: "",
        image: "#",
        linkedin: "",
        github: "",
        portfolio: ""
    },
    {
        name: "",
        role: "",
        image: "#",
        linkedin: "",
        phone: "",
        email: ""
    }
];

// Function to create faculty member card
function createFacultyCard(member) {
    const imageSrc = member.image && member.image.trim() !== "#" ? member.image : "https://photosbull.com/wp-content/uploads/2024/05/no-dp_16.webp";
    return `
        <div class="member-card">
            <div class="member-image-container">
                <img src="${imageSrc}" alt="${member.name}" class="member-image">
            </div>
            <h2 class="member-name">${member.name}</h2>
            <p class="member-role"><i class="fas fa-user-tie"></i> ${member.role}</p>
            <div class="links">
                ${member.phone ? `<a href="tel:${member.phone}" title="Call ${member.name}"><i class="fas fa-phone-alt"></i></a>` : ''}
                ${member.email ? `<a href="mailto:${member.email}" title="Email ${member.name}"><i class="fas fa-envelope"></i></a>` : ''}
                ${member.linkedin ? `<a href="${member.linkedin}" target="_blank" title="LinkedIn Profile"><i class="fab fa-linkedin-in"></i></a>` : ''}
            </div>
        </div>
    `;
}

// Function to create student member card
function createStudentCard(member) {
    const imageSrc = member.image && member.image.trim() !== "#" ? member.image : "https://photosbull.com/wp-content/uploads/2024/05/no-dp_16.webp";
    return `
        <div class="member-card">
            <div class="member-image-container">
                <img src="${imageSrc}" alt="${member.name}" class="member-image">
            </div>
            <h2 class="member-name">${member.name}</h2>
            <p class="member-role"><i class="fas fa-user-graduate"></i> ${member.role}</p>
            <div class="links">
                ${member.phone ? `<a href="tel:${member.phone}" title="Call ${member.name}"><i class="fas fa-phone-alt"></i></a>` : ''}
                ${member.email ? `<a href="mailto:${member.email}" title="Email ${member.name}"><i class="fas fa-envelope"></i></a>` : ''}
                ${member.linkedin ? `<a href="${member.linkedin}" target="_blank" title="LinkedIn Profile"><i class="fab fa-linkedin-in"></i></a>` : ''}
                ${member.github ? `<a href="${member.github}" target="_blank" title="GitHub Profile"><i class="fab fa-github"></i></a>` : ''}
                ${member.portfolio ? `<a href="${member.portfolio}" target="_blank" title="Portfolio Website"><i class="fas fa-link"></i></a>` : ''}
            </div>
        </div>
    `;
}

// Render faculty and student committees
function renderCommittees() {
    const facultyContainer = document.getElementById('faculty-committee');
    const studentContainer = document.getElementById('student-committee');

    facultyContainer.innerHTML = facultyCommittee.map(createFacultyCard).join('');
    studentContainer.innerHTML = studentCommittee.map(createStudentCard).join('');
}

document.addEventListener('DOMContentLoaded', renderCommittees);

document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.member-card');

    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const angleX = (y - centerY) / 30;
            const angleY = (centerX - x) / 30;

            card.style.transform = `perspective(1000px) rotateX(${angleX}deg) rotateY(${angleY}deg) translateZ(10px)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateZ(0)';
        });
    });
});