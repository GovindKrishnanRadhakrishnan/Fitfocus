document.addEventListener('DOMContentLoaded', () => {
    const dobInput = document.querySelector('[name="dob"]');
    const ageInput = document.querySelector('[name="age"]');
    if (dobInput && ageInput) {
        dobInput.addEventListener('change', () => {
            if (!dobInput.value) {
                return;
            }
            const dob = new Date(dobInput.value);
            const today = new Date();
            let age = today.getFullYear() - dob.getFullYear();
            const monthDelta = today.getMonth() - dob.getMonth();
            if (monthDelta < 0 || (monthDelta === 0 && today.getDate() < dob.getDate())) {
                age -= 1;
            }
            if (age >= 0) {
                ageInput.value = age;
            }
        });
    }

    const heightsNode = document.getElementById('member-heights');
    const memberSelect = document.querySelector('#id_member');
    const weightInput = document.querySelector('#id_weight');
    const bmiInput = document.querySelector('#id_bmi');
    if (heightsNode && memberSelect && weightInput && bmiInput) {
        const heights = JSON.parse(heightsNode.textContent);
        const updateBmi = () => {
            const height = Number(heights[memberSelect.value]);
            const weight = Number(weightInput.value);
            if (!height || !weight || height <= 0 || weight <= 0) {
                bmiInput.value = '';
                return;
            }
            const heightM = height / 100;
            bmiInput.value = (weight / (heightM * heightM)).toFixed(1);
        };
        memberSelect.addEventListener('change', updateBmi);
        weightInput.addEventListener('input', updateBmi);
        updateBmi();
    }
});
