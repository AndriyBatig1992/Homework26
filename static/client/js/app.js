token = localStorage.getItem('accessToken')


const contacts = async () => {
    const response = await fetch('http://localhost:8000/api/contacts', {
        method: 'GET',
        headers: {
           Authorization: `Bearer ${token}`,
        },
    })
    console.log(response.status, response.statusText)
    if (response.status === 200) {
       result = await response.json()
       con.innerHTML = ''
       for (contact of result) {
          el = document.createElement('li')
          el.className = 'list-group-item'
          el.innerHTML = `ID: ${contact.id} name:<b> ${contact.first_name}<b> phone:<b> ${contact.phone}<b>`
          con.appendChild(el)
    }
  }
}

contacts()



createForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const response = await fetch('http://localhost:8000/api/contacts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
            first_name: createForm.first_name.value,
            last_name: createForm.last_name.value,
            phone: createForm.phone.value,
            email: createForm.email.value,
        }),
    });
    if (response.status === 201) {
        console.log('Успішно створено контакт');
        contacts();
    } else {
        const errorResponse = await response.json();
        console.error('Помилка при створенні контакту:', errorResponse);
    }
});



const showFormBtn = document.getElementById('showFormBtn');
const hideButtons = document.querySelectorAll('.btn-primary-1');
const row1 = document.querySelector('.row-1');


showFormBtn.addEventListener('mouseover', () => {
    row1.classList.remove('hidden');
});

hideButtons.forEach(button => {
    button.addEventListener('click', () => {
        row1.classList.add('hidden');
    });
});