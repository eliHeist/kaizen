import Alpine from "alpinejs";

Alpine.data('main', () => ({
    destinations: null,
    init() {
        console.log('fetching')
        fetch('/api/destinations/all')
            .then((response) => response.json())
            .then((json) => this.destinations = json);
    },

    // footer
    status: '',
    mail: {
        name: '',
        email: '',
        message: '',
    },
    csrf() {
        return document.getElementById('token')?.firstElementChild?.value;
    },
    sendMail() {
        this.status = 'sending...'
        fetch(`{% url 'contacts:send_mail' %}`, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrf(),
            },
            body: JSON.stringify(this.mail),
        }).then((response) => response.json())
            .then((json) => this.status = json);
        if (status === 'SUCCESS') {
            // clear fields
            this.mail.name = ''
            this.mail.email = ''
            this.mail.message = ''
        }
    }
}))