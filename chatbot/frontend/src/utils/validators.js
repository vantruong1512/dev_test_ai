// Email validation
export function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

// Phone validation (at least 9 digits)
export function validatePhone(phone) {
  const cleaned = phone.replace(/\D/g, '');
  return cleaned.length >= 9;
}

// Required field validation
export function validateRequired(value) {
  return value && value.trim().length > 0;
}
