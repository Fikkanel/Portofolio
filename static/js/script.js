// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Navigation menu toggle for mobile devices
    const menuToggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('nav');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            nav.classList.toggle('active');
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                // Close mobile menu if open
                if (nav.classList.contains('active')) {
                    nav.classList.remove('active');
                }
                
                // Calculate header height for offset
                const headerHeight = document.querySelector('header').offsetHeight;
                
                window.scrollTo({
                    top: targetElement.offsetTop - headerHeight,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Photo gallery filtering
    const filterButtons = document.querySelectorAll('.filter-btn');
    const photoItems = document.querySelectorAll('.photo-item');
    
    if (filterButtons.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
                
                const filter = this.getAttribute('data-filter');
                
                photoItems.forEach(item => {
                    if (filter === 'all' || item.getAttribute('data-category') === filter) {
                        item.style.display = 'block';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        });
    }

    // Photo lightbox
    const photoGallery = document.querySelector('.photos-grid');
    
    if (photoGallery) {
        photoGallery.addEventListener('click', function(e) {
            const photoItem = e.target.closest('.photo-item');
            
            if (photoItem) {
                const imgSrc = photoItem.querySelector('img').src;
                const title = photoItem.querySelector('h3').textContent;
                const description = photoItem.querySelector('p').textContent;
                
                // Create lightbox elements
                const lightbox = document.createElement('div');
                lightbox.className = 'lightbox';
                
                lightbox.innerHTML = `
                    <div class="lightbox-content">
                        <span class="close-lightbox">&times;</span>
                        <img src="${imgSrc}" alt="${title}">
                        <div class="lightbox-caption">
                            <h3>${title}</h3>
                            <p>${description}</p>
                        </div>
                    </div>
                `;
                
                // Add lightbox to body
                document.body.appendChild(lightbox);
                
                // Prevent body scrolling
                document.body.style.overflow = 'hidden';
                
                // Close lightbox on click
                lightbox.addEventListener('click', function(e) {
                    if (e.target.classList.contains('lightbox') || e.target.classList.contains('close-lightbox')) {
                        document.body.removeChild(lightbox);
                        document.body.style.overflow = 'auto';
                    }
                });
            }
        });
    }

    // Add CSS for the lightbox
    const style = document.createElement('style');
    style.textContent = `
        .lightbox {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.9);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 2000;
        }
        
        .lightbox-content {
            position: relative;
            max-width: 80%;
            max-height: 80%;
        }
        
        .lightbox-content img {
            max-width: 100%;
            max-height: 80vh;
            object-fit: contain;
        }
        
        .close-lightbox {
            position: absolute;
            top: -40px;
            right: 0;
            font-size: 30px;
            color: #fff;
            cursor: pointer;
            z-index: 2001;
        }
        
        .lightbox-caption {
            background-color: #fff;
            padding: 15px;
            margin-top: 10px;
        }
    `;
    
    document.head.appendChild(style);

    // Form validation
    const contactForm = document.querySelector('.contact-form form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Simple validation
            const name = this.querySelector('input[name="name"]');
            const email = this.querySelector('input[name="email"]');
            const subject = this.querySelector('input[name="subject"]');
            const message = this.querySelector('textarea[name="message"]');
            let isValid = true;
            
            if (name.value.trim() === '') {
                showError(name, 'Nama tidak boleh kosong');
                isValid = false;
            } else {
                removeError(name);
            }
            
            if (email.value.trim() === '') {
                showError(email, 'Email tidak boleh kosong');
                isValid = false;
            } else if (!isValidEmail(email.value)) {
                showError(email, 'Format email tidak valid');
                isValid = false;
            } else {
                removeError(email);
            }
            
            if (subject.value.trim() === '') {
                showError(subject, 'Subjek tidak boleh kosong');
                isValid = false;
            } else {
                removeError(subject);
            }
            
            if (message.value.trim() === '') {
                showError(message, 'Pesan tidak boleh kosong');
                isValid = false;
            } else {
                removeError(message);
            }
            
            if (isValid) {
                // If form is valid, it would be submitted to the server
                // For now, just show a success message
                const formElements = this.querySelectorAll('input, textarea, button');
                formElements.forEach(element => element.disabled = true);
                
                const successMessage = document.createElement('div');
                successMessage.className = 'success-message';
                successMessage.textContent = 'Pesan Anda telah terkirim. Terima kasih!';
                
                this.appendChild(successMessage);
                
                // Reset form after 3 seconds
                setTimeout(() => {
                    this.reset();
                    formElements.forEach(element => element.disabled = false);
                    this.removeChild(successMessage);
                }, 3000);
            }
        });
    }

    // Helper functions for form validation
    function showError(input, message) {
        const formGroup = input.closest('.form-group');
        const errorElement = formGroup.querySelector('.error-message') || document.createElement('div');
        
        if (!formGroup.querySelector('.error-message')) {
            errorElement.className = 'error-message';
            errorElement.style.color = 'red';
            errorElement.style.fontSize = '0.8rem';
            errorElement.style.marginTop = '5px';
            formGroup.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
        input.style.borderColor = 'red';
    }
    
    function removeError(input) {
        const formGroup = input.closest('.form-group');
        const errorElement = formGroup.querySelector('.error-message');
        
        if (errorElement) {
            formGroup.removeChild(errorElement);
        }
        
        input.style.borderColor = '#ddd';
    }
    
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Add animation on scroll
    const elementsToAnimate = document.querySelectorAll('.section-header, .about-content, .videos-grid, .photos-grid, .contact-content');
    
    function checkScroll() {
        elementsToAnimate.forEach(element => {
            const position = element.getBoundingClientRect();
            
            // If element is in viewport
            if (position.top < window.innerHeight) {
                element.classList.add('animated');
            }
        });
    }
    
    // Add CSS for animations
    const animationStyle = document.createElement('style');
    animationStyle.textContent = `
        .section-header, .about-content, .videos-grid, .photos-grid, .contact-content {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.5s ease, transform 0.5s ease;
        }
        
        .animated {
            opacity: 1;
            transform: translateY(0);
        }
    `;
    
    document.head.appendChild(animationStyle);
    
    // Run on scroll and on initial load
    window.addEventListener('scroll', checkScroll);
    checkScroll();
});