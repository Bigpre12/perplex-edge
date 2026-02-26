self.addEventListener("push", function (event) {
    let payload = { title: "Perplex Edge Alert", body: "New market data arrived." };

    try {
        if (event.data) {
            payload = event.data.json();
        }
    } catch (e) {
        console.warn("Could not parse push payload as JSON:", e);
    }

    const options = {
        body: payload.body,
        icon: "/icon.png", // Assuming an icon exists in public
        badge: "/badge.png", // Small icon for android status bar
        vibrate: [200, 100, 200, 100, 200, 100, 200],
        tag: "perplex-edge-alert",
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1,
        },
    };

    event.waitUntil(self.registration.showNotification(payload.title, options));
});

self.addEventListener("notificationclick", function (event) {
    event.notification.close();
    // Open the primary dashboard when clicked
    event.waitUntil(clients.openWindow("/"));
});
