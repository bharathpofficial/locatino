function sendLocation() {
    const serverUrl = `${window.location.origin}/location`;

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function (position) {
                const latitude = position.coords.latitude;
                const longitude = position.coords.longitude;
                const userAgent = navigator.userAgent;

                // Send location and device details to the server
                fetch(serverUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        latitude: latitude,
                        longitude: longitude,
                        userAgent: userAgent
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    // console.log('Location sent successfully:', data);
                })
                .catch(error => {
                    // console.error('Error sending location:', error);
                });
            },
            function (error) {
                // console.error('Geolocation error:', error);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    } else {
        // console.error('Geolocation is not supported by this browser.');
    }
}