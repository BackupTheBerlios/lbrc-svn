#include <dbus/dbus-glib.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <linux/input.h>
#include <linux/uinput.h>
#include <stdio.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>

// max number of uinput devices we can _parallely_ keep open 
#define MAX_DEVS 256

// array for holding the filedescriptors for the uinput devices
static int uinp_fds[MAX_DEVS];

// helperfunction to find a free array entry for the filedescriptors
// free entries are marked by -1 (a valid filedescriptor should be >= 0)
static int find_free_uinp_entry() {
    int i;
    for(i=0;i<MAX_DEVS;i++) {
        if (uinp_fds[i] == -1) return i;
    }
    return -1;
}

// output functions for errors
static void lose (const char *fmt, ...) G_GNUC_NORETURN G_GNUC_PRINTF (1, 2);
static void lose_gerror (const char *prefix, GError *error) G_GNUC_NORETURN;

static void
lose (const char *str, ...)
{
  va_list args;

  va_start (args, str);

  vfprintf (stderr, str, args);
  fputc ('\n', stderr);

  va_end (args);

  exit (1);
}

static void
lose_gerror (const char *prefix, GError *error) 
{
  lose ("%s: %s", prefix, error->message);
}

typedef struct UInputBridge UInputBridge;
typedef struct UInputBridgeClass UInputBridgeClass;

GType uinputbridge_get_type (void);

struct UInputBridge
{
  GObject parent;
};

struct UInputBridgeClass
{
  GObjectClass parent;
};

#define UINPUTBRIDGE_TYPE_OBJECT              (uinputbridge_get_type ())
#define UINPUTBRIDGE_OBJECT(object)           (G_TYPE_CHECK_INSTANCE_CAST ((object), UINPUTBRIDGE_TYPE_OBJECT, UInputBridge))
#define UINPUTBRIDGE_OBJECT_CLASS(klass)      (G_TYPE_CHECK_CLASS_CAST ((klass), UINPUTBRIDGE_TYPE_OBJECT, UInputBridgeClass))
#define UINPUTBRIDGE_IS_OBJECT(object)        (G_TYPE_CHECK_INSTANCE_TYPE ((object), UINPUTBRIDGE_TYPE_OBJECT))
#define UINPUTBRIDGE_IS_OBJECT_CLASS(klass)   (G_TYPE_CHECK_CLASS_TYPE ((klass), UINPUTBRIDGE_TYPE_OBJECT))
#define UINPUTBRIDGE_OBJECT_GET_CLASS(obj)    (G_TYPE_INSTANCE_GET_CLASS ((obj), UINPUTBRIDGE_TYPE_OBJECT, UInputBridgeClass))

G_DEFINE_TYPE(UInputBridge, uinputbridge, G_TYPE_OBJECT)

static void
uinputbridge_init (UInputBridge *obj)
{
}

static void
uinputbridge_class_init (UInputBridgeClass *klass)
{
}

gboolean
uinputbridge_setup_device (UInputBridge *obj, const char *uinputdevice, 
                           const char *devicename, const guint16 bustype, 
                           gint32 *devid, GError **error)
{
  int i;
  int uinp_fd;
  struct uinput_user_dev uinp;        // uInput device structure
  
  *devid = find_free_uinp_entry();

  if (*devid == -1) return TRUE;

  printf ("UInput Device: %s\n", uinputdevice);
  printf ("Devicename:    %s\n", devicename);
  uinp_fd = open(uinputdevice, O_WRONLY | O_NDELAY);
  if ( uinp_fd == 0 ) {
    printf("Unable to open %s\n", uinputdevice);
    *devid = -1;
    return TRUE;
  }
  memset(&uinp,0,sizeof(uinp));     // Intialize the uInput device to NULL
  strncpy(uinp.name, devicename, UINPUT_MAX_NAME_SIZE);
  uinp.id.bustype = bustype;
  uinp.id.vendor = 1; 
  uinp.id.product = 1;
  uinp.id.version = 0;
  /* The rest of the structure is already set to zero, which is ok, as
     we wont sent abs positions and don't support forcefeedback */

  /* Initialize the event masks, we will use - activate _all_ keyboard keys,
     relative axes, mouse buttons, mouse wheel */
  ioctl(uinp_fd, UI_SET_EVBIT, EV_KEY);
  ioctl(uinp_fd, UI_SET_RELBIT, REL_X);
  ioctl(uinp_fd, UI_SET_RELBIT, REL_Y);
  ioctl(uinp_fd, UI_SET_RELBIT, REL_Z);
  ioctl(uinp_fd, UI_SET_RELBIT, REL_WHEEL);
  for (i=0; i < 256; i++) {
    ioctl(uinp_fd, UI_SET_KEYBIT, i);
  }
  ioctl(uinp_fd, UI_SET_KEYBIT, BTN_MOUSE);
  ioctl(uinp_fd, UI_SET_KEYBIT, BTN_TOUCH);
  ioctl(uinp_fd, UI_SET_KEYBIT, BTN_MOUSE);
  ioctl(uinp_fd, UI_SET_KEYBIT, BTN_LEFT);
  ioctl(uinp_fd, UI_SET_KEYBIT, BTN_MIDDLE);
  ioctl(uinp_fd, UI_SET_KEYBIT, BTN_RIGHT);
  ioctl(uinp_fd, UI_SET_KEYBIT, BTN_FORWARD);
  ioctl(uinp_fd, UI_SET_KEYBIT, BTN_BACK);
  write(uinp_fd, &uinp, sizeof(uinp));
  if (ioctl(uinp_fd, UI_DEV_CREATE)) {
    printf("Unable to create UINPUT device.\n");
    *devid = -1;
    return TRUE;
  } else {
    printf("Successfully created UINPUT device.\n");
    uinp_fds[*devid] = uinp_fd;
    return TRUE;
  }
}

gboolean
uinputbridge_send_event(UInputBridge *obj, gint32 devid, gint16 type, gint16 code, gint32 value)
{
  struct input_event event;           // Input device structure
  memset(&event, 0, sizeof(event));
  gettimeofday(&event.time, NULL);
  event.type = (__u16) type;
  event.code = (__u16) code;
  event.value = (__s32) value;
  write(uinp_fds[devid], &event, sizeof(event));
  return TRUE;
}

gboolean
uinputbridge_close_device (UInputBridge *obj, gint32 devid, GError **error)
{
    close(uinp_fds[devid]);
    printf("Closed UINPUT dev\n");
    uinp_fds[devid] = -1;
    return TRUE;
}

#include "uinputbridge-glue.h"

int
main (int argc, char **argv)
{
  DBusGConnection *bus;
  DBusGProxy *bus_proxy;
  GError *error = NULL;
  UInputBridge *obj;
  GMainLoop *mainloop;
  guint request_name_result;
  int i;

  // clean uinput dev fd array
  for(i=0; i<MAX_DEVS;i++) uinp_fds[i] = -1;

  g_type_init ();

  {
    GLogLevelFlags fatal_mask;
    
    fatal_mask = g_log_set_always_fatal (G_LOG_FATAL_MASK);
    fatal_mask |= G_LOG_LEVEL_WARNING | G_LOG_LEVEL_CRITICAL;
    g_log_set_always_fatal (fatal_mask);
  }
  
  dbus_g_object_type_install_info (UINPUTBRIDGE_TYPE_OBJECT, &dbus_glib_uinputbridge_object_info);

  mainloop = g_main_loop_new (NULL, FALSE);

  bus = dbus_g_bus_get (DBUS_BUS_SESSION, &error);
  if (!bus)
    lose_gerror ("Couldn't connect to session bus", error);

  bus_proxy = dbus_g_proxy_new_for_name (bus, "org.freedesktop.DBus",
					 						  "/org/freedesktop/DBus",
					 						  "org.freedesktop.DBus");

  if (!dbus_g_proxy_call (bus_proxy, "RequestName", &error,
			  G_TYPE_STRING, "org.uinputbridge",
			  G_TYPE_UINT, 0,
			  G_TYPE_INVALID,
			  G_TYPE_UINT, &request_name_result,
			  G_TYPE_INVALID))
    lose_gerror ("Failed to acquire org.uinputbridge", error);

  obj = g_object_new (UINPUTBRIDGE_TYPE_OBJECT, NULL);

  dbus_g_connection_register_g_object (bus, "/UInputBridge", G_OBJECT (obj));

  printf ("service running\n");

  g_main_loop_run (mainloop);

  exit (0);
}
