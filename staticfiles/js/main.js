$(window).on('load', function() {

    /* Alert hide or show script */
    function hideAlert() {
        var alert2 = document.getElementById('alert-2');
        var alert3 = document.getElementById('alert-3');
                
        if (alert2) {
            alert2.style.display = 'none';
        }

        if (alert3) {
            alert3.style.display = 'none';
        }
        
        document.querySelectorAll('.backend-error-message').forEach(function(el) {
            el.style.display = 'none';
        });
    }

    setTimeout(hideAlert, 4000);
});

function openModal(type) {
    if (type == undefined) {
        document.getElementById('suggestionsModal').classList.remove('hidden');
    } else {
        document.getElementById(type+'_suggestionsModal').classList.remove('hidden');
    }
   
}

function closeModal(type) {
    if (type == undefined) {
         document.getElementById('suggestionsModal').classList.add('hidden');
    } else {
        document.getElementById(type+'_suggestionsModal').classList.add('hidden');
    }
}


$(document).ready(function () {


    let debounceTimeout;

    $('#place').on('input', function () {
        searchLocation("general");
    });

    $('#boy_place').on('input', function () {
        searchLocation("boy");
    });
    $('#girl_place').on('input', function () {
        searchLocation("girl");
    });

    async function searchLocation(type) {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(async () => {
            if (type == "general") {
                var searchTerm = document.getElementById("place").value.trim();
            } else {
                var searchTerm = document.getElementById(type+"_place").value.trim();
            }

          
            if (searchTerm.length > 2) {
                try {
               
                    let response = await fetch(`/kundli-preditions/search-location?place=${encodeURIComponent(searchTerm)}`);
               
                    let data = await response.json();    
                 
                    if (type == "general") {
                       var suggestionsDiv = document.getElementById("suggestions");
                    } else {
                       var suggestionsDiv = document.getElementById(type+"_suggestions");
                    }
                 
                    suggestionsDiv.innerHTML = "";

                    if (data.error) {
                        suggestionsDiv.innerHTML = `<div class='suggestion-item'>${data.error}</div>`;
                    } else if (data.length === 0) {
                        suggestionsDiv.innerHTML = `<div class='suggestion-item'>No locations found</div>`;
                    } else {
                        data.forEach(location => {
                            let div = document.createElement("div");
                            div.className = "w-full h-12 rounded-sm bg-gray-100 cursor-pointer p-4";
                            div.textContent = location.place;
                            div.onclick = () => selectLocation(location, type);
                            suggestionsDiv.appendChild(div);
                        });
                        if (type == "general") {
                            openModal();
                        } else {
                            openModal(type);
                        }
                    }
                } catch (error) {
                    console.error("Error fetching locations:", error);
                }
            }
        }, 500);  
    }

    function selectLocation(location, type) {
     
        if (type == "general") {
            document.getElementById("place").value = location.place;
            document.getElementById("latitude").value = location.latitude;
            document.getElementById("longitude").value = location.longitude;
            document.getElementById("suggestions").innerHTML = "";
            closeModal();
        } else {
            document.getElementById(type+"_place").value = location.place;
            document.getElementById(type+"_latitude").value = location.latitude;
            document.getElementById(type+"_longitude").value = location.longitude;
            document.getElementById(type + "_suggestions").innerHTML = "";
            closeModal(type);
        }
        
    }
    
    $('#select-country').on('change', function () {
        let countryId = $(this).val(); // e.g., "IN"
        $.ajax({
            url: '/subscription/states/' + countryId,
            method: "GET",
            success: function (states) {
                let options = '<option value="">-- Select State --</option>';
                for (let stateCode in states) {
                    const state = states[stateCode];
                    options += `<option value="${state.state_code}">${state.name}</option>`;
                }
                $('#select-state').html(options);
            },
            error: function (xhr) {
                console.log("Error loading states:", xhr.responseText);
            }
        });
    });

    $('#select-state').on('change', function () {
        let countryId = $('#select-country').val();
        let stateId = $(this).val();
        $.ajax({
            url: '/subscription/cities/' + countryId+"_"+stateId,
            method: "GET",
            success: function (cities) {
                let options = '<option value="">-- Select City --</option>';
                cities.forEach(city => {
                    options += `<option value="${city}">${city}</option>`;
                });
                $('#select-city').html(options);
            },
            error: function (xhr) {
                console.log("Error loading cities:", xhr.responseText);
            }
        });
    });

    const radioButtons = document.querySelectorAll('input[name="delete_type"]');

    radioButtons.forEach(button => {
        button.addEventListener('change', function () {
            // Reset all circles
            document.querySelectorAll('.circle').forEach(c => {
                c.classList.remove('bg-blue-600', 'bg-red-600');
                c.classList.add('bg-gray-300');
            });

            // Set color based on selection
            const selectedCircle = this.closest('li').querySelector('.circle');
            if (this.value === 'temp') {
                selectedCircle.classList.remove('bg-gray-300');
                selectedCircle.classList.add('bg-blue-600');
            } else if (this.value === 'permanent') {
                selectedCircle.classList.remove('bg-gray-300');
                selectedCircle.classList.add('bg-red-600');
            }
        });
    });


    let sendOtpBtn = document.getElementById("sendOtpBtn");
    if (sendOtpBtn) {
        sendOtpBtn.addEventListener("click", function (event) {
            // Prevent the default form submission behavior
            event.preventDefault();

            
            // Collect form values
            const old_email = document.getElementById("old_email").value;
            const new_email = document.getElementById("new_email").value;
            const password = document.getElementById("password").value;
            const token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

     
            if (!old_email || !new_email || !password) {
                showAlert("All fields are required.", "error");
                return; // Stop further execution if validation fails
            }

            const sendOtpForm = $('#sendOtpForm');
            sendOtpForm.parsley().validate(); // Trigger Parsley validation

            if (sendOtpForm.parsley().isValid()) {
                // Make the fetch request to generate OTP
                fetch("/dashboard/change-email/generate-otp/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": token,
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    body: new URLSearchParams({
                        old_email: old_email,
                        new_email: new_email,
                        password: password
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Success: Show success alert and show verification form
                        showAlert("OTP sent to your email, please check.", "success");
                        document.getElementById("sendOtpForm").style.display = "none";
                        document.getElementById("verifyForm").style.display = "block";
                        document.getElementById("old_email_1").value = old_email;
                        document.getElementById("new_email_1").value = new_email;

                        // Start the cooldown timer for OTP
                        startCooldown();
                    } else {
                        // Failure: Show error alert if the response is not success
                        showAlert("Invalid inputs, please check and try again.", "error");
                    }
                })
                .catch(error => {
                    // Handle errors in the fetch request
                    console.error("Error during OTP generation:", error);
                    showAlert("An error occurred. Please try again later.", "error");
                });

            } else {
                showAlert("Please fill all the fields correctly.", "error");
            }
        });
    }

   
    let verifyOtpBtn = document.getElementById("verifyOtpBtn");

    if (verifyOtpBtn) {
        verifyOtpBtn.addEventListener("click", function (event) {
            // Prevent the default form submission behavior
            event.preventDefault();

            // Collect form values
            const old_email = document.getElementById("old_email_1").value;
            const new_email = document.getElementById("new_email_1").value;
            const old_email_otp = document.getElementById("old_email_otp").value;
            const new_email_otp = document.getElementById("new_email_otp").value;
            const token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

            // Input Validation (Optional: Can be enhanced)
            if (!old_email || !new_email || !old_email_otp || !new_email_otp) {
                showAlert("All fields are required.", "error");
                return; // Stop further execution if validation fails
            }

            const verifyForm = $('#verifyForm');
            verifyForm.parsley().validate(); // Trigger Parsley validation

            if (verifyForm.parsley().isValid()) {
                 // Make the fetch request to verify OTP and change the email
                fetch("/dashboard/change-email/verify-otp/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": token,
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    body: new URLSearchParams({
                        old_email: old_email,
                        new_email: new_email,
                        old_email_otp: old_email_otp,
                        new_email_otp: new_email_otp
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Success: Show success alert and redirect
                        showAlert("Your email has been changed successfully.", "success");
                        window.location.href = "/dashboard/index"; // Redirect to the dashboard
                    } else {
                        // Failure: Show error alert
                        showAlert("Unable to change your email right now. Please try again later.", "error");
                    }
                })
                .catch(error => {
                    // Handle errors in the fetch request
                    console.error("Error during OTP verification:", error);
                    showAlert("Unable to change your email right now. Please try again later.", "error");
                });
                 
            } else {
                showAlert("Please fill all the fields correctly.", "error");
            }
           
        });
    }

   
    function startCooldown() {
        const btn = document.getElementById("sendOtpBtn");
        let cooldown = 60;
        btn.disabled = true;

        const timer = setInterval(() => {
            btn.innerText = `Wait ${cooldown}s`;
            cooldown--;

            if (cooldown < 0) {
                clearInterval(timer);
                btn.innerText = "Send OTP";
                btn.disabled = false;
            }
        }, 1000);
    }

    function showAlert(message, type = 'success') {
      
        const alertBox = document.getElementById("alertBox");
        const alertMessage = document.getElementById("alertMessage");
        alertMessage.textContent = message;
        // Reset classes first
        alertBox.classList.remove("text-green-800", "bg-green-200", "text-red-800", "bg-red-200", "text-yellow-800", "bg-yellow-200");

        if (type === 'error') {
            alertBox.classList.add("text-red-800", "bg-red-200");
        } else if (type === 'warning') {
            alertBox.classList.add("text-yellow-800", "bg-yellow-200");
        } else {
            alertBox.classList.add("text-green-800", "bg-green-200");
        }

        alertBox.classList.remove("hidden");
        setTimeout(() => alertBox.classList.add("hidden"), 4000); 
    }
    function hideAlert() {
       document.getElementById("alertBox").classList.add("hidden");
    }
});


$(document).ready(function () {

    const login_form = $('#login_form');

    if (login_form.length > 0) {
        login_form.parsley().on('form:validate', function (formInstance) {
            if (formInstance.isValid()) {
                login_form.off('submit');  // Prevent recursion
                login_form[0].submit();    // Native submit
            }
        });

        login_form.on('submit', function(e) {
            e.preventDefault(); // Always prevent default
        });
    }

 

    const password_change_form = $('#password_change_form');

    if (password_change_form.length > 0) {
        password_change_form.parsley().on('form:validate', function (formInstance) {
        if (formInstance.isValid()) {
            password_change_form.off('submit');  // Prevent recursion
            password_change_form[0].submit();    // Native submit
        }
        });

        password_change_form.on('submit', function(e) {
            e.preventDefault(); // Always prevent default
        });
    }




    const password_reset_confirm = $('#password_reset_confirm');

    if (password_reset_confirm.length > 0) {
          password_reset_confirm.parsley().on('form:validate', function (formInstance) {
        if (formInstance.isValid()) {
            password_reset_confirm.off('submit');  // Prevent recursion
            password_reset_confirm[0].submit();    // Native submit
            }
        });

        password_reset_confirm.on('submit', function(e) {
            e.preventDefault(); // Always prevent default
        });
    }

 

    const forget_password_form = $('#forget_password');

    if (forget_password_form.length > 0) {
        forget_password_form.parsley().on('form:validate', function (formInstance) {
            if (formInstance.isValid()) {
                forget_password_form.off('submit');  // Prevent recursion
                forget_password_form[0].submit();    // Native submit
            }
        });

        forget_password_form.on('submit', function(e) {
            e.preventDefault(); // Always prevent default
        });
    }

  

    const register_form = $('#register_form');

    if (register_form.length > 0) {
    
        register_form.parsley().on('form:validate', function (formInstance) {
            if (formInstance.isValid()) {
                register_form.off('submit');  // Prevent recursion
                register_form[0].submit();    // Native submit
            }
        });

        register_form.on('submit', function (e) {
            e.preventDefault(); // Always prevent default
        });
    }


    const verify_otp_form = $('#verify_otp_form');

    if (verify_otp_form.length > 0) { 
        verify_otp_form.parsley().on('form:validate', function (formInstance) {
            if (formInstance.isValid()) {
                verify_otp_form.off('submit');  // Prevent recursion
                verify_otp_form[0].submit();    // Native submit
            }
        });
        verify_otp_form.on('submit', function(e) {
            e.preventDefault(); // Always prevent default
        });
    }    

    const account_form = $('#account_form');

    if (account_form.length > 0) { 
        account_form.parsley().on('form:validate', function (formInstance) {
            if (formInstance.isValid()) {
                account_form.off('submit');  // Prevent recursion
                account_form[0].submit();    // Native submit
            }
        });
        account_form.on('submit', function(e) {
            e.preventDefault(); // Always prevent default
        });
    }   

    const profile_form = $('#profile_form');

    if (profile_form.length > 0) { 
        profile_form.parsley().on('form:validate', function (formInstance) {
            if (formInstance.isValid()) {
                profile_form.off('submit');  // Prevent recursion
                profile_form[0].submit();    // Native submit
            }
        });
        profile_form.on('submit', function(e) {
            e.preventDefault(); // Always prevent default
        });
    }   

    const disable_2fa_form = $("#disable_2fa_form");
    if (disable_2fa_form.length > 0) { 
        disable_2fa_form.parsley().on('form:validate', function (formInstance) {
            if (formInstance.isValid()) {
                disable_2fa_form.off('submit');  // Prevent recursion
                disable_2fa_form[0].submit();   
            }
        });
        disable_2fa_form.on('submit', function(e) {
            e.preventDefault(); // Always prevent default
        });
    }

        
    const enable_2fa_form = $('#enable_2fa_form');
    if (enable_2fa_form.length > 0) {
        enable_2fa_form.parsley().on('form:validate', function (formInstance) {
            if (formInstance.isValid()) {
                // Submit the form after validation passes
                enable_2fa_form.off('submit').submit();  // This ensures the form is submitted
                enable_2fa_form[0].submit();   
            }
        });
        
        enable_2fa_form.on('submit', function(e) {
            e.preventDefault(); // Always prevent default, but we’ll manually trigger the submission after validation
        });
    }


    const verify_otp_form_2fa = $('#verify_otp_form_2fa');
    if (verify_otp_form_2fa.length > 0) { 
        verify_otp_form_2fa.parsley().on('form:validate', function (formInstance) {
            if (formInstance.isValid()) {
                verify_otp_form_2fa.off('submit');  // Prevent recursion
                verify_otp_form_2fa[0].submit();   
            }
        });
        verify_otp_form_2fa.on('submit', function(e) {
            e.preventDefault(); // Always prevent default
        });
    }

    const kundli_matching_form =  $('#kundli_matching_form');
    if (kundli_matching_form.length > 0) { 
        kundli_matching_form.parsley().on('form:validate', function (formInstance) {
            if (formInstance.isValid()) {
                kundli_matching_form.off('submit');  // Prevent recursion
                kundli_matching_form[0].submit();   
            }
        });
        kundli_matching_form.on('submit', function(e) {
            e.preventDefault(); // Always prevent default
        });
    }

    const dasha_form =  $('#dasha_form');
    if (dasha_form.length > 0) { 
        dasha_form.parsley().on('form:validate', function (formInstance) {
            if (formInstance.isValid()) {
                dasha_form.off('submit');  // Prevent recursion
                dasha_form[0].submit();  
            }
        });
        dasha_form.on('submit', function(e) {
            e.preventDefault(); // Always prevent default
        });
    }


    const contact_form =  $('#contact_form');
    if (contact_form.length > 0) { 
        contact_form.parsley().on('form:validate', function (formInstance) {
            if (formInstance.isValid()) {
                contact_form.off('submit');  // Prevent recursion
                contact_form[0].submit();  
            }
        });
        contact_form.on('submit', function(e) {
            e.preventDefault(); // Always prevent default
        });
    }
    

    const kundli_form =  $('#kundli_form');
    if (kundli_form.length > 0) { 
        kundli_form.parsley().on('form:validate', function (formInstance) {
            if (formInstance.isValid()) {
                kundli_form.off('submit');  // Prevent recursion
                kundli_form[0].submit();  
            }
        });
        kundli_form.on('submit', function(e) {
            e.preventDefault(); // Always prevent default
        });
    }


    const loshugrid_form =  $('#loshugrid_form');
    if (loshugrid_form.length > 0) { 
        loshugrid_form.parsley().on('form:validate', function (formInstance) {
            if (formInstance.isValid()) {
                loshugrid_form.off('submit');  // Prevent recursion
                loshugrid_form[0].submit();  
            }
        });
        loshugrid_form.on('submit', function(e) {
            e.preventDefault(); // Always prevent default
        });
    }


    const name_number_form =  $('#name_number_form');
    if (name_number_form.length > 0) { 
        name_number_form.parsley().on('form:validate', function (formInstance) {
            if (formInstance.isValid()) {
                name_number_form.off('submit');  // Prevent recursion
                name_number_form[0].submit(); 
            }
        });
        name_number_form.on('submit', function(e) {
            e.preventDefault(); // Always prevent default
        });
    }
    
    const panchang_form =  $('#panchang_form');
    if (panchang_form.length > 0) { 
        panchang_form.parsley().on('form:validate', function (formInstance) {
            if (formInstance.isValid()) {
                panchang_form.off('submit');  // Prevent recursion
                panchang_form[0].submit(); 
            }
        });
        panchang_form.on('submit', function(e) {
            e.preventDefault(); // Always prevent default
        });
    }

    const checkout_form =  $('#checkout_form');
    if (checkout_form.length > 0) { 
        checkout_form.parsley().on('form:validate', function (formInstance) {
            if (formInstance.isValid()) {
                checkout_form.off('submit');  // Prevent recursion
                checkout_form[0].submit(); 
            }
        });
        checkout_form.on('submit', function(e) {
            e.preventDefault(); // Always prevent default
        });
    }
        
    $('#refresh_capcha').click(function () {
        $.getJSON("/captcha/refresh/", function (result) {
            $('.captcha').attr('src', result['image_url']);
            $('#id_captcha_0').val(result['key']);
        });
    });

     $('#user-menu-button').on('click', function () {
        $('#user-menu-list').toggle();
    });

    $('.menu-item').on('click', function () {
        $('#user-menu-list').hide();
    });

    const menuToggle = document.getElementById("menu-toggle");
    const menuList = document.getElementById("mobile-menu-list");
    const hamburger = document.getElementById("hamburger");
    const closeIcon = document.getElementById("close");

    menuToggle.addEventListener("click", () => {
        menuList.classList.toggle("hidden");
        hamburger.classList.toggle("hidden");
        closeIcon.classList.toggle("hidden");
    });

});

$('#user-menu-button').on('click', function (e) {
    e.stopPropagation();
});



$(document).on('click', function (e) {
    if (!$(e.target).closest('#user-menu-button, #user-menu-list').length) {
        $('#user-menu-list').hide();
       
    }
});
