(function() {
  "use strict";

  var APP = {
    token: null,
    user: null,
    trophy: null,
    scene: null,
    camera: null,
    renderer: null,
    controls: null,
    mesh: null,
    points: [],
    lines: null,
    raycaster: null,
    mouse: null,
    isOrthographic: false,
    selectedTrophyId: null,
    draftId: null,
    pointIdCounter: 0,
    animationId: null,
    gridHelper: null,
    axesHelper: null,
    lights: [],
    pointType: "vertex",
    cameraGroup: null,

    init: function() {
      console.log("APP.init() called");
      var self = this;
      var storedToken = localStorage.getItem("token");
      if (storedToken) {
        self.token = storedToken;
        self.getCurrentUser(function(user) {
          if (user) { self.showMainApp(); return; }
          self.showLogin();
        });
      } else { self.showLogin(); }
      self.bindEvents();
    },
    login: function(email, password) {
      var self = this;
      return APP.api("/api/v1/auth/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({email: email, password: password})
      }).then(function(res) {
        self.token = res.token;
        localStorage.setItem("token", res.token);
        return APP.getCurrentUser();
      });
    },
    register: function(username, email, password) {
      var self = this;
      return APP.api("/api/v1/auth/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username: username, email: email, password: password})
      }).then(function(res) {
        self.token = res.token;
        localStorage.setItem("token", res.token);
        return APP.getCurrentUser();
      });
    },
    logout: function() {
      this.token = null;
      this.user = null;
      this.trophy = null;
      localStorage.removeItem("token");
      if (this.renderer) { this.renderer.dispose(); }
      if (this.animationId) { cancelAnimationFrame(this.animationId); }
      this.showLogin();
    },
    getCurrentUser: function(callback) {
      var self = this;
      return APP.api("/api/v1/users/me", {
        method: "GET"
      }).then(function(res) {
        self.user = res;
        if (callback) callback(res);
        return res;
      }).catch(function() {
        if (callback) callback(null);
        return null;
      });
    },
    api: function(endpoint, options) {
      var self = this;
      var headers = options.headers || {};
      if (self.token) {
        headers["Authorization"] = "Bearer " + self.token;
      }
      options.headers = headers;
      return fetch(endpoint, options)
        .then(function(response) {
          if (!response.ok) {
            if (response.status === 401) {
              APP.logout();
              throw new Error("Unauthorized");
            }
            return response.text().then(function(text) {
              throw new Error(text || "API Error " + response.status);
            });
          }
          var contentType = response.headers.get("Content-Type");
          if (contentType && contentType.includes("application/json")) {
            return response.json();
          }
          return response.text();
        })
        .catch(function(err) {
          console.error("API Error:", err);
          throw err;
        });
    },
    showLogin: function() {
      var els = {
        login: document.getElementById("login-section"),
        register: document.getElementById("register-section"),
        trophies: document.getElementById("trophies-section"),
        detail: document.getElementById("trophy-detail"),
        logout: document.getElementById("btn-logout")
      };
      if(els.login) els.login.classList.remove("hidden");
      if(els.register) els.register.classList.add("hidden");
      if(els.trophies) els.trophies.classList.add("hidden");
      if(els.detail) els.detail.classList.add("hidden");
      if(els.logout) els.logout.classList.add("hidden");
    },
    showRegister: function() {
      var els = {
        login: document.getElementById("login-section"),
        register: document.getElementById("register-section"),
        trophies: document.getElementById("trophies-section"),
        detail: document.getElementById("trophy-detail")
      };
      if(els.login) els.login.classList.add("hidden");
      if(els.register) els.register.classList.remove("hidden");
      if(els.trophies) els.trophies.classList.add("hidden");
      if(els.detail) els.detail.classList.add("hidden");
    },
    showMainApp: function() {
      var els = {
        login: document.getElementById("login-section"),
        register: document.getElementById("register-section"),
        trophies: document.getElementById("trophies-section"),
        detail: document.getElementById("trophy-detail"),
        logout: document.getElementById("btn-logout")
      };
      if(els.login) els.login.classList.add("hidden");
      if(els.register) els.register.classList.add("hidden");
      if(els.trophies) els.trophies.classList.remove("hidden");
      if(els.detail) els.detail.classList.add("hidden");
      if(els.logout) els.logout.classList.remove("hidden");
      APP.loadTrophies();
    },
    loadTrophies: function() {
      var self = this;
      return APP.api("/api/v1/trophies", { method: "GET" })
        .then(function(trophies) {
          var container = document.getElementById("trophies-container");
          if (!container) return;
          container.innerHTML = "";
          if (!trophies || trophies.length === 0) {
            container.innerHTML = '<p class="text-gray-500">No trophies found. Create one!</p>';
            return;
          }
          trophies.forEach(function(t) {
            var card = document.createElement("div");
            card.className = "card";
            card.innerHTML = '<h3 class="font-semibold mb-2">' + (t.name || "Untitled") + '</h3>';
            if (t.status) card.innerHTML += '<span class="badge">' + t.status + '</span>';
            card.style.cursor = "pointer";
            card.addEventListener("click", function() { APP.selectTrophy(t.id); });
            container.appendChild(card);
          });
        })
        .catch(function(err) { console.error("Load trophies error:", err); });
    },
    createTrophy: function(data) {
      return APP.api("/api/v1/trophies", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
      });
    },
    selectTrophy: function(id) {
      var self = this;
      self.selectedTrophyId = id;
      return APP.api("/api/v1/trophies/" + id, { method: "GET" })
        .then(function(trophy) {
          self.trophy = trophy;
          var nameEl = document.getElementById("trophy-name");
          if (nameEl) nameEl.textContent = trophy.name || "Untitled";
          var statusEl = document.getElementById("trophy-status");
          if (statusEl) statusEl.textContent = trophy.status || "";
          var els = {
            trophies: document.getElementById("trophies-section"),
            detail: document.getElementById("trophy-detail")
          };
          if(els.trophies) els.trophies.classList.add("hidden");
          if(els.detail) els.detail.classList.remove("hidden");
          self.initScene();
        })
        .catch(function(err) { console.error("Select trophy error:", err); });
    },
    initScene: function() {
      var self = this;
      var viewer = document.getElementById("viewer");
      if (!viewer) return;
      if (self.renderer) { viewer.removeChild(self.renderer.domElement); self.renderer.dispose(); }
      if (self.animationId) { cancelAnimationFrame(self.animationId); }
      var width = viewer.clientWidth;
      var height = viewer.clientHeight;
      self.scene = new THREE.Scene();
      self.scene.background = new THREE.Color(0x1a1a2e);
      self.camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
      self.camera.position.set(5, 5, 5);
      self.camera.lookAt(0, 0, 0);
      self.renderer = new THREE.WebGLRenderer({ antialias: true });
      self.renderer.setSize(width, height);
      self.renderer.setPixelRatio(window.devicePixelRatio);
      viewer.appendChild(self.renderer.domElement);
      self.gridHelper = new THREE.GridHelper(10, 10, 0x444444, 0x222222);
      self.scene.add(self.gridHelper);
      self.axesHelper = new THREE.AxesHelper(3);
      self.scene.add(self.axesHelper);
      self.setupLights();
      self.setupControls();
      self.raycaster = new THREE.Raycaster();
      self.mouse = new THREE.Vector2();
      self.startAnimationLoop();
      var onResize = function() {
        var w = viewer.clientWidth;
        var h = viewer.clientHeight;
        self.camera.aspect = w / h;
        self.camera.updateProjectionMatrix();
        self.renderer.setSize(w, h);
      };
      window.addEventListener("resize", onResize);
    },
    setupLights: function() {
      var self = this;
      self.lights.forEach(function(l) { self.scene.remove(l); });
      self.lights = [];
      var dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
      dirLight.position.set(5, 10, 7);
      self.scene.add(dirLight);
      self.lights.push(dirLight);
      var ambientLight = new THREE.AmbientLight(0x404060, 0.6);
      self.scene.add(ambientLight);
      self.lights.push(ambientLight);
    },
    loadSTL: function(file) {
      var self = this;
      if (!file) return Promise.reject(new Error("No file provided"));
      var reader = new FileReader();
      return new Promise(function(resolve, reject) {
        reader.onload = function(e) {
          try {
            if (self.mesh) { self.scene.remove(self.mesh); self.mesh = null; }
            var loader = new THREE.STLLoader();
            var geometry = loader.parse(new Uint8Array(e.target.result));
            var material = new THREE.MeshPhongMaterial({ color: 0x3b82f6, shininess: 100 });
            self.mesh = new THREE.Mesh(geometry, material);
            self.mesh.position.set(0, 0, 0);
            self.scene.add(self.mesh);
            var box = new THREE.BoxGeometry(1, 1, 1);
            box.copy(geometry.boundingBox);
            var center = geometry.boundingBox.center();
            self.mesh.position.sub(center);
            resolve(self.mesh);
          } catch(err) { reject(err); }
        };
        reader.onerror = function() { reject(reader.error); };
        reader.readAsArrayBuffer(file);
      });
    },
    setupControls: function() {
      var self = this;
      if (self.controls) { self.controls.dispose(); }
      var controlsEl = document.getElementById("viewer");
      if (!controlsEl) return;
      if (THREE.OrbitControls) {
        self.controls = new THREE.OrbitControls(self.camera, self.renderer.domElement);
        self.controls.enableDamping = true;
        self.controls.dampingFactor = 0.05;
        self.controls.screenSpacePanning = true;
        self.controls.update();
      }
    },
    toggleWireframe: function() {
      if (!this.mesh) return;
      this.mesh.traverse(function(child) {
        if (child.isMesh) {
          child.material.wireframe = !child.material.wireframe;
        }
      });
    },
    resetCamera: function() {
      this.camera.position.set(5, 5, 5);
      this.camera.lookAt(0, 0, 0);
      if (this.controls) { this.controls.target.set(0, 0, 0); this.controls.update(); }
    },
    setView: function(preset) {
      var self = this;
      var positions = {
        front: { pos: [0, 0, 10], look: [0, 0, 0] },
        back: { pos: [0, 0, -10], look: [0, 0, 0] },
        left: { pos: [-10, 0, 0], look: [0, 0, 0] },
        right: { pos: [10, 0, 0], look: [0, 0, 0] },
        top: { pos: [0, 10, 0.01], look: [0, 0, 0] },
        bottom: { pos: [0, -10, 0], look: [0, 0, 0] }
      };
      var view = positions[preset];
      if (!view) return;
      self.camera.position.set(view.pos[0], view.pos[1], view.pos[2]);
      self.camera.lookAt(view.look[0], view.look[1], view.look[2]);
      if (self.controls) { self.controls.target.set(view.look[0], view.look[1], view.look[2]); self.controls.update(); }
    },
    toggleOrthographic: function() {
      var self = this;
      self.isOrthographic = !self.isOrthographic;
      var w = self.renderer.domElement.clientWidth;
      var h = self.renderer.domElement.clientHeight;
      var size = 10;
      var newCamera;
      if (self.isOrthographic) {
        var aspect = w / h;
        newCamera = new THREE.OrthographicCamera(-size * aspect, size * aspect, size, -size, 0.1, 1000);
        newCamera.position.copy(self.camera.position);
        newCamera.rotation.copy(self.camera.rotation);
      } else {
        newCamera = new THREE.PerspectiveCamera(60, w / h, 0.1, 1000);
        newCamera.position.copy(self.camera.position);
        newCamera.rotation.copy(self.camera.rotation);
      }
      newCamera.lookAt(0, 0, 0);
      self.camera = newCamera;
      if (self.controls) { self.controls.object = self.camera; self.controls.update(); }
      if (self.scene) self.scene.add(self.camera);
    },
    placePoint: function(type, position) {
      var self = this;
      var point = { id: ++self.pointIdCounter, type: type, position: position.clone(), element: null };
      self.points.push(point);
      var geo = new THREE.SphereGeometry(0.1, 16, 16);
      var color = type === "vertex" ? 0x10b981 : (type === "edge" ? 0xf59e0b : 0xef4444);
      var mat = new THREE.MeshBasicMaterial({ color: color });
      var sphere = new THREE.Mesh(geo, mat);
      sphere.position.copy(position);
      sphere.userData = { pointId: point.id };
      self.scene.add(sphere);
      point.element = sphere;
      self.updatePointsVisual();
      return point;
    },
    updatePointsVisual: function() {
      var self = this;
      if (self.lines) { self.scene.remove(self.lines); }
      if (self.points.length >= 2) {
        var positions = [];
        self.points.forEach(function(p) { positions.push(p.position); });
        var geo = new THREE.BufferGeometry().setFromPoints(positions);
        var mat = new THREE.LineBasicMaterial({ color: 0x3b82f6, linewidth: 2 });
        self.lines = new THREE.Line(geo, mat);
        self.scene.add(self.lines);
      }
      self.calculateMeasurements();
      self.updateResults();
    },
    calculateMeasurements: function() {
      var self = this;
      var l = 0, w = 0;
      if (self.points.length >= 2) {
        var first = self.points[0].position;
        var last = self.points[self.points.length - 1].position;
        l = first.distanceTo(last);
      }
      if (self.points.length >= 3) {
        var d1 = self.points[0].position.distanceTo(self.points[1].position);
        var d2 = self.points[1].position.distanceTo(self.points[2].position);
        w = Math.sqrt(d1 * d1 + d2 * d2 - 2 * d1 * d2 * Math.cos(Math.PI / 2));
      }
      self._length = l;
      self._width = w;
      self._total = l + w;
    },
    updateResults: function() {
      var lenEl = document.getElementById("result-length");
      var wEl = document.getElementById("result-width");
      var totalEl = document.getElementById("result-total");
      if (lenEl) lenEl.textContent = (self._length || 0).toFixed(2) + " m";
      if (wEl) wEl.textContent = (self._width || 0).toFixed(2) + " m";
      if (totalEl) totalEl.textContent = (self._total || 0).toFixed(2) + " m";
    },
    saveDraft: function() {
      var self = this;
      if (!self.selectedTrophyId) return Promise.reject(new Error("No trophy selected"));
      var data = {
        trophyId: self.selectedTrophyId,
        points: self.points.map(function(p) { return { type: p.type, x: p.position.x, y: p.position.y, z: p.position.z }; }),
        measurements: { length: self._length || 0, width: self._width || 0, total: self._total || 0 }
      };
      return APP.api("/api/v1/drafts", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
      }).then(function(res) {
        self.draftId = res.id;
        alert("Draft saved successfully");
        return res;
      });
    },
    submitForReview: function() {
      var self = this;
      if (!self.selectedTrophyId) return Promise.reject(new Error("No trophy selected"));
      return APP.api("/api/v1/trophies/" + self.selectedTrophyId + "/review", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ action: "submit" })
      }).then(function(res) {
        alert("Submitted for review!");
        return res;
      });
    },
    downloadPDF: function() {
      if (!self.selectedTrophyId) return;
      var url = "/api/v1/trophies/" + self.selectedTrophyId + "/pdf";
      var link = document.createElement("a");
      link.href = url;
      link.download = "trophy_report.pdf";
      link.click();
    },
    startAnimationLoop: function() {
      var self = this;
      function animate() {
        self.animationId = requestAnimationFrame(animate);
        if (self.controls) self.controls.update();
        if (self.renderer && self.scene && self.camera) {
          self.renderer.render(self.scene, self.camera);
        }
      }
      animate();
    },
    bindEvents: function() {
      var self = this;
      var loginBtn = document.getElementById("btn-login");
      if (loginBtn) loginBtn.addEventListener("click", function(e) {
        e.preventDefault();
        var email = document.getElementById("login-email").value.trim();
        var password = document.getElementById("login-password").value;
        if (!email || !password) { alert("Please fill in all fields"); return; }
        APP.login(email, password).then(function() { APP.showMainApp(); }).catch(function(err) { alert("Login failed: " + err.message); });
      });
      var regBtn = document.getElementById("btn-register");
      if (regBtn) regBtn.addEventListener("click", function(e) {
        e.preventDefault();
        var username = document.getElementById("reg-username").value.trim();
        var email = document.getElementById("reg-email").value.trim();
        var password = document.getElementById("reg-password").value;
        if (!username || !email || !password) { alert("Please fill in all fields"); return; }
        APP.register(username, email, password).then(function() { APP.showMainApp(); }).catch(function(err) { alert("Registration failed: " + err.message); });
      });
      var showReg = document.getElementById("show-register");
      if (showReg) showReg.addEventListener("click", function(e) { e.preventDefault(); APP.showRegister(); });
      var showLogin = document.getElementById("show-login");
      if (showLogin) showLogin.addEventListener("click", function(e) { e.preventDefault(); APP.showLogin(); });
      var logoutBtn = document.getElementById("btn-logout");
      if (logoutBtn) logoutBtn.addEventListener("click", function() { APP.logout(); });
      var newTrophyBtn = document.getElementById("btn-new-trophy");
      if (newTrophyBtn) newTrophyBtn.addEventListener("click", function() {
        APP.createTrophy({ name: "New Trophy", status: "draft" }).then(function(t) { APP.selectTrophy(t.id); });
      });
      var backBtn = document.getElementById("btn-back");
      if (backBtn) backBtn.addEventListener("click", function() { APP.loadTrophies(); });
      var wireframeBtn = document.getElementById("btn-wireframe");
      if (wireframeBtn) wireframeBtn.addEventListener("click", function() { APP.toggleWireframe(); });
      var resetBtn = document.getElementById("btn-reset-camera");
      if (resetBtn) resetBtn.addEventListener("click", function() { APP.resetCamera(); });
      var fileInput = document.getElementById("file-input");
      if (fileInput) fileInput.addEventListener("change", function(e) { APP.handleFileUpload(e); });
      var saveBtn = document.getElementById("btn-save");
      if (saveBtn) saveBtn.addEventListener("click", function() { APP.saveDraft().catch(function(err) { alert("Save failed: " + err.message); }); });
      var submitBtn = document.getElementById("btn-submit");
      if (submitBtn) submitBtn.addEventListener("click", function() { APP.submitForReview().catch(function(err) { alert("Submit failed: " + err.message); }); });
      var pdfBtn = document.getElementById("btn-pdf");
      if (pdfBtn) pdfBtn.addEventListener("click", function() { APP.downloadPDF(); });
      var viewer = document.getElementById("viewer");
      if (viewer) {
        viewer.addEventListener("click", function(e) { APP.handlePointClick(e); });
        viewer.addEventListener("mousemove", function(e) { APP.onMouseMove(e); });
        viewer.addEventListener("mouseup", function(e) { APP.onMouseUp(e); });
      }
    },
    handleFileUpload: function(input) {
      var file = input.files && input.files[0];
      if (!file) return;
      APP.loadSTL(file).then(function() {
        APP.resetCamera();
      }).catch(function(err) { alert("Failed to load STL: " + err.message); });
    },
    handlePointClick: function(event) {
      var self = this;
      var viewer = document.getElementById("viewer");
      if (!viewer) return;
      var rect = viewer.getBoundingClientRect();
      self.mouse.x = ((event.clientX - rect.left) / viewer.clientWidth) * 2 - 1;
      self.mouse.y = -((event.clientY - rect.top) / viewer.clientHeight) * 2 + 1;
      self.raycaster.setFromCamera(self.mouse, self.camera);
      if (self.mesh) {
        var intersects = self.raycaster.intersectObject(self.mesh, true);
        if (intersects.length > 0) {
          var point = intersects[0].point.clone();
          self.placePoint(self.pointType, point);
        }
      }
    },
    onMouseMove: function(event) {
      var self = this;
      if (!self.renderer || !self.camera) return;
      var viewer = document.getElementById("viewer");
      if (!viewer) return;
      var rect = viewer.getBoundingClientRect();
      self.mouse.x = ((event.clientX - rect.left) / viewer.clientWidth) * 2 - 1;
      self.mouse.y = -((event.clientY - rect.top) / viewer.clientHeight) * 2 + 1;
    },
    onMouseUp: function(event) {
      // Placeholder for drag events
    },
    self._total = 0;
  // ============================================
  // EXTRA HELPERS
  // ============================================
  clearScene: function() {
    var self = this;
    if (self.mesh) { self.scene.remove(self.mesh); self.mesh = null; }
    if (self.lines) { self.scene.remove(self.lines); self.lines = null; }
    self.points = [];
    self.pointIdCounter = 0;
    self._length = 0;
    self._width = 0;
    self._total = 0;
    var toRemove = [];
    self.scene.traverse(function(child) {
      if (child.userData && child.userData.pointId) { toRemove.push(child); }
    });
    toRemove.forEach(function(child) { self.scene.remove(child); });
    self.updateResults();
  };

  selectPointType: function(type) {
    var valid = ["vertex", "edge", "face"];
    if (valid.indexOf(type) !== -1) {
      APP.pointType = type;
    }
  };

  removeLastPoint: function() {
    var self = this;
    if (self.points.length === 0) return;
    var last = self.points.pop();
    if (last.element) { self.scene.remove(last.element); }
    self.updatePointsVisual();
  };

  clearAllPoints: function() {
    var self = this;
    self.points.forEach(function(p) {
      if (p.element) self.scene.remove(p.element);
    });
    self.points = [];
    self.pointIdCounter = 0;
    if (self.lines) { self.scene.remove(self.lines); self.lines = null; }
    self._length = 0;
    self._width = 0;
    self._total = 0;
    self.updateResults();
  };

  getPointCount: function() {
    return APP.points.length;
  };

  setCameraPosition: function(x, y, z) {
    APP.camera.position.set(x, y, z);
    if (APP.controls) { APP.controls.update(); }
  };

  focusOnTrophy: function() {
    if (!APP.mesh) return;
    var box = new THREE.Box3().setFromObject(APP.mesh);
    var center = box.center();
    var size = box.size();
    var maxDim = Math.max(size.x, size.y, size.z);
    var fov = APP.camera.fov * (Math.PI / 180);
    var cameraZ = maxDim / (2 * Math.tan(fov / 2));
    var distance = cameraZ * 1.5;
    APP.camera.position.set(center.x + distance, center.y + distance, center.z + distance);
    APP.camera.lookAt(center);
    if (APP.controls) { APP.controls.target.copy(center); APP.controls.update(); }
  };
  };

  // Initialize app when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function() { APP.init(); });
  } else {
    APP.init();
  }

  // Expose APP globally
  window.APP = APP;
})();
