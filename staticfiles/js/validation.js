window.Parsley.addValidator('custompassword', {
  requirementType: 'string',
  validateString: function (value) {
    const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return passwordPattern.test(value);
  },
  messages: {
    en: 'Password must be at least 8 characters long, include uppercase, lowercase, a number, and a special character.'
  }
});

// Custom Email Validator
window.Parsley.addValidator('customemail', {
  requirementType: 'string',
  validateString: function (value) {
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailPattern.test(value);
  },
  messages: {
    en: 'Please enter a valid email address.'
  }
});

window.Parsley.addValidator('customotp', {
  requirementType: 'string',
  validateString: function (value) {
    const otpPattern = /^\d{6}$/; // Only allows exactly 6 digits
    return otpPattern.test(value);
  },
  messages: {
    en: 'Please enter a valid 6-digit OTP.'
  }
});

window.Parsley.addValidator('customname', {
  requirementType: 'string',
  validateString: function (value) {
    const namePattern = /^[a-zA-Z]{2,}$/;  // Only letters and spaces, minimum 2 chars
    return namePattern.test(value);
  },
  messages: {
    en: 'Please enter a valid name (only letters, at least 2 characters).'
  }
});




window.Parsley.addValidator('customfullname', {
  requirementType: 'string',
  validateString: function (value) {
    const namePattern = /^[a-zA-Z ]{2,}$/;
    return namePattern.test(value.trim());
  },
  messages: {
    en: 'Please enter a valid name (only letters and spaces, at least 2 characters).'
  }
});

window.Parsley.addValidator('notfuturedate', {
  validateString: function (value) {
    const inputDate = new Date(value);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return inputDate <= today;
  },
  messages: {
    en: 'Birth date cannot be in the future.'
  }
});

window.Parsley.addValidator('username', {
  requirementType: 'string',
  validateString: function (value) {
    const usernamePattern = /^[a-zA-Z0-9]+$/; // only letters and numbers
    return usernamePattern.test(value);
  },
  messages: {
    en: 'Username can only contain letters and numbers, no spaces.'
  }
});


window.Parsley.addValidator('profileFile', {
  requirementType: 'string',
  validateString: function (value, requirement) {
    // Check if file is selected (i.e., input value is not empty)
    if (!value) {
      return true;  // It's optional, so if no file is selected, it's valid
    }

    // Get the file input element
    const fileInput = document.querySelector('input[name="profile"]');
    const file = fileInput.files[0];

    if (file) {
      // Allowed file types (image/jpeg, image/png, pdf)
      const allowedTypes = ['image/jpeg', 'image/png'];
      // Max file size limit (5MB)
      const maxSize = 1 * 1024 * 1024; // 1MB in bytes

      // Check file type
      if (!allowedTypes.includes(file.type)) {
        return false;  // Invalid file type
      }

      // Check file size
      if (file.size > maxSize) {
        return false;  // Invalid file size
      }
    }

    return true; // Valid if file is selected and checks pass
  },
  messages: {
    en: 'Please select a valid file (JPEG, PNG, and less than 1MB).'
  }
});


window.Parsley.addValidator('place', {
  requirementType: 'string',
  validateString: function (value) {
    const birthplacePattern = /^[a-zA-Z0-9\s,]+$/; // Letters, numbers, spaces, and commas
    return birthplacePattern.test(value);
  },
  messages: {
    en: 'Birth place can only contain letters, numbers, spaces, and commas.'
  }
});

window.Parsley.addValidator('message', {
  requirementType: 'string',
  validateString: function (value) {
    // Allow letters, numbers, spaces, and common punctuation
    const messagePattern = /^[a-zA-Z0-9\s.,!?'"()\-:;@#&]+$/;
    return messagePattern.test(value.trim());
  },
  messages: {
    en: 'Message can only contain letters, numbers, spaces, and basic punctuation.'
  }
});


window.Parsley.addValidator('phone', {
  requirementType: 'string',
  validateString: function (value) {
    // Allows optional + at the start, followed by 10 to 15 digits
    const phonePattern = /^\+?[0-9]{10,15}$/;
    return phonePattern.test(value.trim());
  },
  messages: {
    en: 'Please enter a valid phone number (10 to 12 digits).'
  }
});