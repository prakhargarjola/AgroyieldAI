document.addEventListener("DOMContentLoaded", () => {
  const forecastBtn = document.getElementById("forecast-btn");
  const dashboardSection = document.getElementById("dashboard");
  const form = document.getElementById("forecast-form");
  const resultBox = document.getElementById("result-box");


  function createAutocomplete(inputId, datalistId) {
    const input = document.getElementById(inputId);
    const datalist = document.getElementById(datalistId);
    if (!input || !datalist) return;

    const options = Array.from(datalist.options).map(opt => opt.value);

    
    const buildList = (filter) => {
      closeAllLists();
      
      const listContainer = document.createElement("DIV");
      listContainer.setAttribute("id", input.id + "autocomplete-list");
      listContainer.setAttribute("class", "autocomplete-items");
      input.parentNode.appendChild(listContainer);

      options.forEach(option => {
        if (option.toUpperCase().includes(filter.toUpperCase())) {
          const item = document.createElement("DIV");
          const matchIndex = option.toUpperCase().indexOf(filter.toUpperCase());
          item.innerHTML = option.substring(0, matchIndex) +
                           "<strong>" + option.substring(matchIndex, matchIndex + filter.length) + "</strong>" +
                           option.substring(matchIndex + filter.length);
          item.innerHTML += "<input type='hidden' value='" + option + "'>";
          
          item.addEventListener("click", function (e) {
            input.value = this.getElementsByTagName("input")[0].value;
            closeAllLists();
          });
          listContainer.appendChild(item);
        }
      });
    };

    
    input.addEventListener("click", function(e) {
        e.stopPropagation(); 
        buildList("");
    });
    
    
    input.addEventListener("input", function (e) {
      buildList(this.value);
    });

    
    input.addEventListener("keydown", function(e) {
        const list = document.getElementById(this.id + "autocomplete-list");
        if (list) {
            if (e.key === "Enter") {
                e.preventDefault(); 
                const items = list.getElementsByTagName("div");
                if (items.length > 0) {
                    items[0].click(); 
                }
            }
        }
    });

    
    const closeAllLists = (elmnt) => {
      const items = document.getElementsByClassName("autocomplete-items");
      for (let i = 0; i < items.length; i++) {
        
        if (elmnt != items[i]) {
          items[i].parentNode.removeChild(items[i]);
        }
      }
    }

    
    document.addEventListener("click", function (e) {
      closeAllLists(e.target);
    });
  }

  
  createAutocomplete("district", "district-list");
  createAutocomplete("crop", "crop-list");

 

  if (forecastBtn && dashboardSection) {
    forecastBtn.addEventListener("click", () => {
      dashboardSection.scrollIntoView({ behavior: "smooth" });
    });
  }

  
  if (form && resultBox) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      
      const district = document.getElementById("district").value.trim();
      const crop = document.getElementById("crop").value.trim();
      const year = document.getElementById("year").value.trim();
      const area = document.getElementById("area").value.trim();
      
      if (!district || !crop || !year || !area) {
        resultBox.innerHTML = `<p style="color:red;">⚠️ Please fill in all fields.</p>`;
        return;
      }
      
      resultBox.innerHTML = `<p>🧠 Analyzing data and generating recommendations...</p>`;

      try {
        const formData = new FormData();
        formData.append("district", district);
        formData.append("crop", crop);
        formData.append("year", year);
        formData.append("area", area);
        
        const response = await fetch("/predict", { method: "POST", body: formData });
        const data = await response.json();
        
        if (data.error) {
          resultBox.innerHTML = `<p style="color:red;">❌ Error: ${data.error}</p>`;
          return;
        }

        let resultHTML = `
          <h3>📊 Yield Forecast Result</h3>
          <div class="result-details">
            <span><strong>District:</strong> ${data.district}</span>
            <span><strong>Crop:</strong> ${data.crop}</span>
            <span><strong>Year:</strong> ${data.year}</span>
            <span><strong>Area:</strong> ${data.area} ha</span>
          </div>
          <hr>
          
          <h2 style="color:#2d6a4f;">Predicted Yield: ${(data.predicted_yield / 100).toFixed(2)} quintal/ha</h2>
          
          <h3 class="revenue-display">Estimated Revenue: ₹${data.predicted_revenue.toLocaleString('en-IN')}/ha</h3>

          <p class="weather-info">
            🌦️ Weather Source: ${data.weather.source.toUpperCase()} | 
            Avg Temp: ${data.weather.temp_avg}°C | 
            Rainfall: ${data.weather.rainfall} mm
          </p>
        `;

        if (data.recommendations && data.recommendations.length > 0) {
          resultHTML += `
            <div class="recommendations-container">
              <h4>🌱 Other Profitable Crop Recommendations</h4>
              <div class="rec-cards">
          `;
          data.recommendations.forEach(rec => {
            resultHTML += `
              <div class="rec-card">
                <h5>${rec.crop}</h5>
                <p><strong>Revenue:</strong> ₹${rec.revenue.toLocaleString('en-IN')}/ha</p>
                <p><strong>Yield:</strong> ${(rec.yield / 100).toFixed(2)} quintal/ha</p>
                <p><strong>Irrigation:</strong> ${rec.irrigation} mm</p>
              </div>
            `;
          });
          resultHTML += `
              </div>
            </div>
          `;
        }
        resultBox.innerHTML = resultHTML;

      } catch (err) {
        resultBox.innerHTML = `<p style="color:red;">⚠️ Backend not responding. Please try again later.</p>`;
      }
    });
  }

  
  const sections = document.querySelectorAll("section");
  const navLinks = document.querySelectorAll("nav ul li a");
  
  window.addEventListener("scroll", () => {
    let current = "";
    sections.forEach((section) => {
      const sectionTop = section.offsetTop - 80;
      if (scrollY >= sectionTop) {
        current = section.getAttribute("id");
      }
    });

    navLinks.forEach((link) => {
      link.classList.remove("active");
      if (link.getAttribute("href") === `#${current}`) {
        link.classList.add("active");
      }
    });
  });
});

document.addEventListener("DOMContentLoaded", () => {
  
  const termsModal = document.getElementById("terms-modal");
  const privacyModal = document.getElementById("privacy-modal");

  const termsLink = document.getElementById("terms-link");
  const privacyLink = document.getElementById("privacy-link");

  const closeTermsBtn = document.getElementById("close-terms");
  const closePrivacyBtn = document.getElementById("close-privacy");

  
  const openModal = (modal) => {
    if (modal) modal.style.display = "block";
  };

  
  const closeModal = (modal) => {
    if (modal) modal.style.display = "none";
  };

  
  if (termsLink) termsLink.addEventListener("click", (e) => {
    e.preventDefault();
    openModal(termsModal);
  });

  if (privacyLink) privacyLink.addEventListener("click", (e) => {
    e.preventDefault();
    openModal(privacyModal);
  });

  
  if (closeTermsBtn) closeTermsBtn.addEventListener("click", () => closeModal(termsModal));
  if (closePrivacyBtn) closePrivacyBtn.addEventListener("click", () => closeModal(privacyModal));

  
  window.addEventListener("click", (e) => {
    if (e.target == termsModal) closeModal(termsModal);
    if (e.target == privacyModal) closeModal(privacyModal);
  });
});

document.getElementById("predictForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    const response = await fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    const result = await response.json();

    document.getElementById("predictionResult").innerText =
        `Predicted Yield: ${result.prediction.toFixed(2)} Kg/ha`;

    
    document.getElementById("explanationResult").innerText = result.explanation;
});
