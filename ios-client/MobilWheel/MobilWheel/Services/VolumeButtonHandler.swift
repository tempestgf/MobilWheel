import AVFoundation
import MediaPlayer
import UIKit

/// Intercepts physical volume button presses and fires callbacks
/// instead of changing the system volume.
final class VolumeButtonHandler: ObservableObject {
    var onVolumeUp: (() -> Void)?
    var onVolumeDown: (() -> Void)?

    private var observation: NSKeyValueObservation?
    private let session = AVAudioSession.sharedInstance()
    private let midVolume: Float = 0.5
    private var hiddenVolumeView: MPVolumeView?
    private var isResetting = false

    func start() {
        // Activate audio session so we can observe volume
        try? session.setActive(true)
        try? session.setCategory(.playback, options: .mixWithOthers)

        // Reset volume to mid-point so we can detect both up and down
        isResetting = true
        setSystemVolume(midVolume)

        // Observe outputVolume changes
        observation = session.observe(\.outputVolume, options: [.new, .old]) { [weak self] _, change in
            guard let self, let newVol = change.newValue, let oldVol = change.oldValue else { return }
            DispatchQueue.main.async {
                // Ignore changes from our own reset
                guard !self.isResetting else {
                    self.isResetting = false
                    return
                }
                if newVol > oldVol {
                    self.onVolumeUp?()
                } else if newVol < oldVol {
                    self.onVolumeDown?()
                }
                // Reset to midpoint so buttons keep working at extremes
                self.isResetting = true
                self.setSystemVolume(self.midVolume)
            }
        }

        // Place a hidden MPVolumeView so the system HUD doesn't appear
        installHiddenVolumeView()
    }

    func stop() {
        observation?.invalidate()
        observation = nil
        hiddenVolumeView?.removeFromSuperview()
        hiddenVolumeView = nil
    }

    deinit { stop() }

    private func setSystemVolume(_ value: Float) {
        guard let slider = hiddenVolumeView?.subviews.compactMap({ $0 as? UISlider }).first else { return }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.01) {
            slider.value = value
        }
    }

    private func installHiddenVolumeView() {
        guard let windowScene = UIApplication.shared.connectedScenes
            .compactMap({ $0 as? UIWindowScene }).first,
              let window = windowScene.windows.first else { return }

        let volumeView = MPVolumeView(frame: CGRect(x: -1000, y: -1000, width: 1, height: 1))
        volumeView.alpha = 0.01
        window.addSubview(volumeView)
        hiddenVolumeView = volumeView
    }
}
