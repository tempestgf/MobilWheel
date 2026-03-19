import sys

xml_path = r"C:\Users\Tempestgf\Coding\MobileWheel\android-client\app\src\main\res\layout\activity_dashboard.xml"

with open(xml_path, 'r', encoding='utf-8') as f:
    text = f.read()

# I will insert a custom TrackMapView or a simple FrameLayout to hold the map trail.
insertion_point = text.rfind('</RelativeLayout>')

map_xml = """
    <!-- TRACK MAP VIEW -->
    <com.tempestgf.steeringwheel.TrackMapView
        android:id="@+id/trackMapView"
        android:layout_width="150dp"
        android:layout_height="150dp"
        android:layout_alignParentBottom="true"
        android:layout_alignParentEnd="true"
        android:layout_marginEnd="40dp"
        android:layout_marginBottom="40dp"
        android:elevation="6dp" />
"""

if "TrackMapView" not in text:
    new_text = text[:insertion_point] + map_xml + text[insertion_point:]
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Map view injected into XML.")
else:
    print("Already injected.")
