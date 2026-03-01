self.addEventListener('push', function(event) {
  const data = event.data ? event.data.json() : {};
  
  const options = {
    body: data.body || 'New update from Journey Buddi',
    icon: data.icon || '/icons/buddi-192.png',
    badge: data.badge || '/icons/buddi-badge-72.png',
    data: data.data || {},
    tag: data.tag,
    renotify: !!data.tag,
    actions: [],
  };

  if (data.data && data.data.type === 'swap') {
    options.actions = [
      { action: 'view', title: 'View Suggestion' },
      { action: 'dismiss', title: 'Dismiss' },
    ];
  }

  event.waitUntil(
    self.registration.showNotification(data.title || 'Journey Buddi', options)
  );
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();

  const data = event.notification.data || {};
  let url = '/';

  if (data.type === 'briefing' && data.trip_id) {
    url = `/trip/${data.trip_id}/today`;
  } else if (data.type === 'swap' && data.trip_id) {
    url = `/trip/${data.trip_id}/today`;
  } else if (data.type === 'condition_alert' && data.trip_id) {
    url = `/trip/${data.trip_id}/today`;
  }

  event.waitUntil(
    clients.matchAll({ type: 'window' }).then(function(clientList) {
      for (const client of clientList) {
        if (client.url.includes(data.trip_id) && 'focus' in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(url);
      }
    })
  );
});
