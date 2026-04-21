"""
==============================================================================
test_login.py — Test Suite untuk LoginPage
==============================================================================

Menguji komponen LoginPage (src/ui/login.py).
Fixture `login_page` tersedia via tests/ui/conftest.py.
==============================================================================
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit


# ===========================================================================
# SECTION 2: TEST — LoginPage
# ===========================================================================

class TestLoginPage:
    """Kumpulan tes untuk komponen LoginPage (src/ui/login.py)."""

    def test_widget_terbuat_dan_terlihat(self, login_page):
        """
        Memastikan LoginPage berhasil diinstansiasi dan widget utama ada.
        Widget harus memiliki atribut text_input dan login_button.
        """
        widget, _ = login_page
        assert widget is not None
        assert hasattr(widget, "text_input"), "LoginPage harus memiliki atribut text_input"
        assert hasattr(widget, "login_button"), "LoginPage harus memiliki atribut login_button"

    def test_text_input_adalah_qlineedit(self, login_page):
        """
        Memastikan text_input adalah instance QLineEdit dengan EchoMode Password
        (karena ini field kunci/password).
        """
        widget, _ = login_page
        assert isinstance(widget.text_input, QLineEdit)
        assert widget.text_input.echoMode() == QLineEdit.EchoMode.Password

    def test_ketik_teks_pada_input(self, qtbot, login_page):
        """
        Simulasi pengguna mengetik teks pada field input menggunakan
        qtbot.keyClicks(). Memastikan teks berhasil masuk ke widget.
        """
        widget, _ = login_page
        widget.show()
        qtbot.keyClicks(widget.text_input, "123456")
        assert widget.text_input.text() == "123456"

    def test_login_gagal_input_bukan_angka(self, qtbot, login_page):
        """
        Memastikan pesan error muncul ketika pengguna mengetik teks bukan angka
        (misalnya huruf) lalu mengklik tombol login.
        """
        widget, MockDB = login_page
        widget.show()
        widget.text_input.setText("abc")
        qtbot.mouseClick(widget.login_button, Qt.MouseButton.LeftButton)
        assert "Kunci Hanya Berupa Angka" in widget.error_info.text()

    def test_login_berhasil_memanggil_callback(self, qtbot, login_page):
        """
        Memastikan on_login_success callback dipanggil ketika login berhasil.
        DatabaseManager.verify_login di-mock untuk mengembalikan (True, {...}).
        """
        widget, MockDB = login_page
        fake_user = {"nama": "Tester", "role": "Admin"}
        MockDB.return_value.verify_login.return_value = (True, fake_user)
        widget.show()
        widget.text_input.setText("123456")
        qtbot.mouseClick(widget.login_button, Qt.MouseButton.LeftButton)
        widget.on_login_success.assert_called_once_with(fake_user)

    def test_login_gagal_menampilkan_pesan_error(self, qtbot, login_page):
        """
        Memastikan pesan error dari DB ditampilkan di label error_info
        ketika verify_login mengembalikan (False, pesan_error).
        """
        widget, MockDB = login_page
        MockDB.return_value.verify_login.return_value = (False, "Kunci salah!")
        widget.show()
        widget.text_input.setText("999999")
        qtbot.mouseClick(widget.login_button, Qt.MouseButton.LeftButton)
        assert "Kunci salah!" in widget.error_info.text()

    def test_toggle_password_visibility(self, qtbot, login_page):
        """
        Memastikan toggle_visibility_button mengubah EchoMode dari Password
        ke Normal dan sebaliknya.
        """
        widget, _ = login_page
        widget.show()
        # Kondisi awal: password tersembunyi
        assert widget.text_input.echoMode() == QLineEdit.EchoMode.Password
        qtbot.mouseClick(widget.toggle_visibility_button, Qt.MouseButton.LeftButton)
        # Setelah klik: seharusnya Normal
        assert widget.text_input.echoMode() == QLineEdit.EchoMode.Normal
        qtbot.mouseClick(widget.toggle_visibility_button, Qt.MouseButton.LeftButton)
        # Setelah klik ke-2: kembali Password
        assert widget.text_input.echoMode() == QLineEdit.EchoMode.Password

    def test_session_info_mengubah_teks(self, login_page):
        """
        Memastikan metode session_info() mengubah teks label error_info.
        Digunakan untuk menampilkan informasi sesi yang sudah berakhir.
        """
        widget, _ = login_page
        widget.session_info("Sesi telah berakhir. Silakan login ulang.")
        assert "Sesi telah berakhir" in widget.error_info.text()
