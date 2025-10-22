document.getElementById("menu-toggle").addEventListener("click", function(e) {
  e.preventDefault();
  document.getElementById("wrapper").classList.toggle("toggled");
});

document.addEventListener('DOMContentLoaded', function() {
  setTimeout(function() {
    let alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
      let bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    });
  }, 5000);
});

document.addEventListener('click', function(e) {
  if (e.target.classList.contains('btn-delete')) {
    if (!confirm('Tem certeza que deseja excluir este item?')) {
      e.preventDefault();
    }
  }
});