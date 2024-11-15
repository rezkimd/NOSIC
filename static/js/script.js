document.addEventListener("DOMContentLoaded", function () {
  const links = document.querySelectorAll(".sidebar a");
  const tabContents = document.querySelectorAll(".tab-content");

  links.forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      tabContents.forEach((content) => content.classList.remove("active"));
      const target = document.getElementById(this.id.replace("-link", ""));
      target.classList.add("active");

      if (this.id === "user-data-link") {
        fetchUserData();
      }
    });
  });

  // Simulating camera stream
  const videoElement = document.getElementById("video");
  navigator.mediaDevices
    .getUserMedia({ video: true })
    .then((stream) => {
      videoElement.srcObject = stream;
    })
    .catch((error) => {
      console.error("Error accessing the camera", error);
    });

  function fetchUserData() {
    fetch("/api/userdata")
      .then((response) => response.json())
      .then((data) => {
        const userDataContainer = document.getElementById("user-data");
        userDataContainer.innerHTML = "<h3>User Data</h3>";
        data.forEach((user) => {
          userDataContainer.innerHTML += `<p>ID: ${user.id}, Name: ${user.name}, Email: ${user.email}</p>`;
        });
      })
      .catch((error) => console.error("Error fetching user data:", error));
  }

  // Sending updated settings to the server
  function updateSettings(settings) {
    fetch("/api/settings", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(settings),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data.message);
      })
      .catch((error) => {
        console.error("Error updating settings:", error);
      });
  }
});
