var map = L.map('map').setView([36.3393, -97.9131], 10);

function rxNextTOMessage(chatSocket) {

    chatSocket.addEventListener('message', function(e){

        let msg = JSON.parse(e.data)
        if(msg.type == 'nextTOMessage' && msg.runway == "KEND 17L/35R"){
                let data = msg.data
                document.getElementById('nextTO--solo').checked = data.solo
                document.getElementById('nextTO--formationX2').checked = data.formationX2
                document.getElementById('nextTO--formationX4').checked = data.formationX4
        }
    })
}

function nextTOMessage(chatSocket, id) {
    solo = document.getElementById('nextTO--solo').checked
    formationX2 = document.getElementById('nextTO--formationX2').checked
    formationX4 = document.getElementById('nextTO--formationX4').checked

    if(formationX2 == true && id == 'formationX4') {
        formationX4 = false
    }

    if(formationX4 == true && id == 'formationX2') {
        formationX2 = false
    }

    console.log(window.location.href)
    chatSocket.send(JSON.stringify({
      'type': 'nextTOMessage',
      'runway': 'KEND 17L/35R',
      'data': {
        'solo': solo,
        'formationX2': formationX2,
        'formationX4': formationX4
      }
  }))
}



function load(chatSocket, csrf_token) {

    //var map = L.map('map').setView([36.3393, -97.9131], 13);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    L.marker([36.3393, -97.9131]).addTo(map)
        .bindPopup('KEND')
        .openPopup();

    var MapAcft = {}
    var MapAcftNotUpdated = []

    let legacyT6Icon = L.icon({
        iconUrl: '../../../static/AutoRecorder/images/LegacyT6Icon.png',
        //shadowUrl: '../static/AutoRecorder/leaflet/images/marker-shadow.png',

        iconSize:     [30, 30], // size of the icon
        shadowSize:   [20, 20], // size of the shadow
        iconAnchor:   [15, 15], // point of the icon which will correspond to marker's location
        shadowAnchor: [0, 0],  // the same for the shadow
        popupAnchor:  [0, -30] // point from which the popup should open relative to the iconAnchor

    })

    let inactiveLegacyT6Icon = L.icon({
        iconUrl: '../../../static/AutoRecorder/images/40-LegacyT6Icon.png',
        //shadowUrl: '../static/AutoRecorder/leaflet/images/marker-shadow.png',

        iconSize:     [30, 30], // size of the icon
        shadowSize:   [20, 20], // size of the shadow
        iconAnchor:   [15, 15], // point of the icon which will correspond to marker's location
        shadowAnchor: [0, 0],  // the same for the shadow
        popupAnchor:  [0, -30] // point from which the popup should open relative to the iconAnchor

    })

    let UFO = L.icon({
        iconUrl: '../../../static/AutoRecorder/images/UFO.png',
        //shadowUrl: '../static/AutoRecorder/leaflet/images/marker-shadow.png',

        iconSize:     [20, 20], // size of the icon
        shadowSize:   [20, 20], // size of the shadow
        iconAnchor:   [10, 10], // point of the icon which will correspond to marker's location
        shadowAnchor: [0, 0],  // the same for the shadow
        popupAnchor:  [0, -30] // point from which the popup should open relative to the iconAnchor

    })

    let inactiveUFO = L.icon({
        iconUrl: '../../../static/AutoRecorder/images/30-UFO.png',
        //shadowUrl: '../static/AutoRecorder/leaflet/images/marker-shadow.png',

        iconSize:     [30, 30], // size of the icon
        shadowSize:   [20, 20], // size of the shadow
        iconAnchor:   [15, 15], // point of the icon which will correspond to marker's location
        shadowAnchor: [0, 0],  // the same for the shadow
        popupAnchor:  [0, -30] // point from which the popup should open relative to the iconAnchor

    })

    
    chatSocket.addEventListener('message', function(e){
        let data = JSON.parse(e.data)

        if(data.type == 'rwyUpdate'){

            let rwyUpdate = JSON.parse(data.message)
            let t6Meta = JSON.parse(data.meta)
            console.log("HELLLOOOOOOOOOOOOOO")


            let Pattern = document.getElementById(' In Pattern')
            removeAllChildNodes(Pattern)
            let Taxiing = document.getElementById(' Taxiing')
            removeAllChildNodes(Taxiing)
            let OffStation = document.getElementById(' Off Station')
            removeAllChildNodes(OffStation)
            let LostSignal = document.getElementById(' Lost Signal')
            removeAllChildNodes(LostSignal)
            let numPattern = document.getElementById('num In Pattern')
            removeAllChildNodes(numPattern)
            let numTaxiing = document.getElementById('num Taxiing')
            removeAllChildNodes(numTaxiing)
            let numOffStation = document.getElementById('num Off Station')
            removeAllChildNodes(numOffStation)
            let numLostSignal = document.getElementById('num Lost Signal')
            removeAllChildNodes(numLostSignal)


            let dual145 = document.getElementById(' Dual Aircraft Outside the Pattern > 1+45')
            removeAllChildNodes(dual145)
            let solo120 = document.getElementById(' Solo Aircraft Outside the Pattern > 1+20')
            removeAllChildNodes(solo120)
            let solosOffStation = document.getElementById(' Solos Off Station')
            removeAllChildNodes(solosOffStation)
            let solosInPattern = document.getElementById(' Solos in the Pattern')
            removeAllChildNodes(solosInPattern)

            let numdual145 = document.getElementById('num Dual Aircraft Outside the Pattern > 1+45')
            removeAllChildNodes(numdual145)
            let numsolo120 = document.getElementById('num Solo Aircraft Outside the Pattern > 1+20')
            removeAllChildNodes(numsolo120)
            let numsolosOffStation = document.getElementById('num Solos Off Station')
            removeAllChildNodes(numsolosOffStation)
            let numsolosInPattern = document.getElementById('num Solos in the Pattern')
            removeAllChildNodes(numsolosInPattern)

            numdual145.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.dual145.length}</span>
            `)
            
            numsolo120.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.solo120.length}</span>
            `)
            
            numsolosOffStation.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.solosOffStation.length}</span>
            `)
            
            numsolosInPattern.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.solosInPattern.length}</span>
            `)

            //update the badge displaying the number of aircraft in each major state
            if(t6Meta.In_Pattern < 8) { //blue background
                numPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-primary rounded-pill">${t6Meta.In_Pattern}</span>
                `)
            }
            else if (t6Meta.In_Pattern >= 12) { //red background
                numPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-danger rounded-pill">${t6Meta.In_Pattern}</span>
                `)
            }
            else { //yellow background
                numPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-warning rounded-pill">${t6Meta.In_Pattern}</span>
                `)
            }

            numTaxiing.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.Taxiing}</span>
            `)

            numOffStation.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.Off_Station}</span>
            `)

            numLostSignal.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.Lost_Signal}</span>
            `)

            for (let i = 0; i < t6Meta.dual145.length; i++) {
                dual145.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-secondary">${t6Meta.dual145[i]}</span>
                `
                )   
            }

            for (let i = 0; i < t6Meta.solo120.length; i++) {
                solo120.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-danger">${t6Meta.solo120[i]}</span>
                `
                )   
            }

            for (let i = 0; i < t6Meta.solosOffStation.length; i++) {
                solosOffStation.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-warning">${t6Meta.solosOffStation[i]}</span>
                `
                )   
            }

            for (let i = 0; i < t6Meta.solosInPattern.length; i++) {
                solosInPattern.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-info">${t6Meta.solosInPattern[i]}</span>
                `
                )   
            }

            MapAcftNotUpdated = {...MapAcft}
            console.log(MapAcftNotUpdated)
                            
            for (let i = 0; i < rwyUpdate.length; i++) {

                delete MapAcftNotUpdated[rwyUpdate[i].pk]

                let formX2Checkmark = ""
                let formX4Checkmark = ""
                let soloCheckmark = ""
                if (rwyUpdate[i].fields.solo) {soloCheckmark = "checked"}
                if (rwyUpdate[i].fields.formationX2) {formX2Checkmark = "checked"}
                if (rwyUpdate[i].fields.formationX4) {formX4Checkmark = "checked"}
                

                if (rwyUpdate[i].fields.substate == "eastside") {
                    if (!MapAcft[rwyUpdate[i].pk]) {
                        // If there is no marker with this id yet, instantiate a new one.;

                        if(rwyUpdate[i].fields.aircraftType != "TEX2") {
                            //If it's not a T-6, then it's a UFO!
                            MapAcft[rwyUpdate[i].pk] = L.marker([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude], {rotationAngle: rwyUpdate[i].fields.track, icon: UFO}).addTo(map).bindPopup(rwyUpdate[i].fields.callSign);
                        }
                        else { //It's a T-6...
                            MapAcft[rwyUpdate[i].pk] = L.marker([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude], {rotationAngle: rwyUpdate[i].fields.track, icon: legacyT6Icon}).addTo(map).bindPopup(rwyUpdate[i].fields.callSign);
                        }
                          
                      } else {
                        // If there is already a marker with this id, simply modify its position.
                        MapAcft[rwyUpdate[i].pk].setLatLng([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude]).setRotationAngle(rwyUpdate[i].fields.track).setPopupContent(rwyUpdate[i].fields.callSign);

                        if(rwyUpdate[i].fields.aircraftType != "TEX2") {
                            //If it's not a T-6, then it's a UFO!
                            MapAcft[rwyUpdate[i].pk].setIcon(UFO);
                        }
                        else { //It's a T-6...
                            MapAcft[rwyUpdate[i].pk].setIcon(legacyT6Icon);
                        }
                      }

                    Pattern.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="dashboard/edit/${rwyUpdate[i].pk}" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${rwyUpdate[i].pk.slice(-3)}</td>
                            <td>${rwyUpdate[i].fields.callSign}</td>
                            <td>${rwyUpdate[i].fields.alt_baro}</td>
                            <td>${rwyUpdate[i].fields.groundSpeed}</td>
                            <td>${String(rwyUpdate[i].fields.takeoffTime).slice(11, -8).concat(String(rwyUpdate[i].fields.takeoffTime).slice(23))}</td>
                            <td>${String(rwyUpdate[i].fields.landTime).slice(11, -8).concat(String(rwyUpdate[i].fields.landTime).slice(23))}</td>

                            <td style="padding-top: 0px; padding-bottom: 0px; white-space: nowrap;">
                                <table><tr><td>
                                    <form method="POST" action="${window.location.href}/formX2/${rwyUpdate[i].pk}" class="form-group">    
                                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                        <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${formX2Checkmark}>  
                                        <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">2-Ship</label>     
                                    </form>
                                </td></tr>
                                <tr><td>
                                    <form method="POST" action="${window.location.href}/formX4/${rwyUpdate[i].pk}" class="form-group">
                                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                        <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${formX4Checkmark}>  
                                        <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">4-Ship</label>
                                    </form>
                                </td></tr></table>
                            </td>

                            <td>
                            <form method="POST" action="${window.location.href}/solo/${rwyUpdate[i].pk}" class="form-group">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${soloCheckmark}>  
                                <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">Solo</label>
                            </form>
                            </td>

                            <td><center><a href="dashboard/355/${rwyUpdate[i].pk}" class="btn btn-primary btn-sm btn-danger">355</a></center></td>
                            </tr>`
                            )

                }
                if (rwyUpdate[i].fields.state == "taxiing") {
                    if (!MapAcft[rwyUpdate[i].pk]) {
                        // If there is no marker with this id yet, instantiate a new one.;

                        if(rwyUpdate[i].fields.aircraftType != "TEX2") {
                            //If it's not a T-6, then it's a UFO!
                            MapAcft[rwyUpdate[i].pk] = L.marker([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude], {rotationAngle: rwyUpdate[i].fields.track, icon: inactiveUFO}).addTo(map).bindPopup(rwyUpdate[i].fields.callSign);
                        }
                        else { //It's a T-6...
                            MapAcft[rwyUpdate[i].pk] = L.marker([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude], {rotationAngle: rwyUpdate[i].fields.track, icon: inactiveLegacyT6Icon}).addTo(map).bindPopup(rwyUpdate[i].fields.callSign);
                        }
                          
                    } else {
                        // If there is already a marker with this id, simply modify its position.
                        MapAcft[rwyUpdate[i].pk].setLatLng([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude]).setRotationAngle(rwyUpdate[i].fields.track).setPopupContent(rwyUpdate[i].fields.callSign);

                        if(rwyUpdate[i].fields.aircraftType != "TEX2") {
                            //If it's not a T-6, then it's a UFO!
                            MapAcft[rwyUpdate[i].pk].setIcon(inactiveUFO);
                        }
                        else { //It's a T-6...
                            MapAcft[rwyUpdate[i].pk].setIcon(inactiveLegacyT6Icon);
                        }
                      }

                    Taxiing.insertAdjacentHTML('beforeend',       
                    `<tr>
                    <th scope="row"><a href="dashboard/edit/${rwyUpdate[i].pk}" class="btn btn-primary btn-sm">edit</a></th>
                    <td>${rwyUpdate[i].pk.slice(-3)}</td>
                    <td>${rwyUpdate[i].fields.callSign}</td>
                    <td>${rwyUpdate[i].fields.alt_baro}</td>
                    <td>${rwyUpdate[i].fields.groundSpeed}</td>
                    <td>${String(rwyUpdate[i].fields.takeoffTime).slice(11, -8).concat(String(rwyUpdate[i].fields.takeoffTime).slice(23))}</td>
                    <td>${String(rwyUpdate[i].fields.landTime).slice(11, -8).concat(String(rwyUpdate[i].fields.landTime).slice(23))}</td>

                    <td style="padding-top: 0px; padding-bottom: 0px; white-space: nowrap;">
                        <table><tr><td>
                            <form method="POST" action="${window.location.href}/formX2/${rwyUpdate[i].pk}" class="form-group">    
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${formX2Checkmark}>  
                                <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">2-Ship</label>     
                            </form>
                        </td></tr>
                        <tr><td>
                            <form method="POST" action="${window.location.href}/formX4/${rwyUpdate[i].pk}" class="form-group">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${formX4Checkmark}>  
                                <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">4-Ship</label>
                            </form>
                        </td></tr></table>
                    </td>

                    <td>
                    <form method="POST" action="${window.location.href}/solo/${rwyUpdate[i].pk}" class="form-group">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                        <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${soloCheckmark}>  
                        <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">Solo</label>
                    </form>
                    </td>

                    <td><center><a href="dashboard/355/${rwyUpdate[i].pk}" class="btn btn-primary btn-sm btn-danger">355</a></center></td>
                    </tr>`
                    )
                }
                if (rwyUpdate[i].fields.state == "off station") {
                    if (!MapAcft[rwyUpdate[i].pk]) {
                        // If there is no marker with this id yet, instantiate a new one.;

                        if(rwyUpdate[i].fields.aircraftType != "TEX2") {
                            //If it's not a T-6, then it's a UFO!
                            MapAcft[rwyUpdate[i].pk] = L.marker([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude], {rotationAngle: rwyUpdate[i].fields.track, icon: UFO}).addTo(map).bindPopup(rwyUpdate[i].fields.callSign);
                        }
                        else { //It's a T-6...
                            MapAcft[rwyUpdate[i].pk] = L.marker([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude], {rotationAngle: rwyUpdate[i].fields.track, icon: legacyT6Icon}).addTo(map).bindPopup(rwyUpdate[i].fields.callSign);
                        }
                          
                    } else {
                        // If there is already a marker with this id, simply modify its position.
                        MapAcft[rwyUpdate[i].pk].setLatLng([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude]).setRotationAngle(rwyUpdate[i].fields.track).setPopupContent(rwyUpdate[i].fields.callSign);

                        if(rwyUpdate[i].fields.aircraftType != "TEX2") {
                            //If it's not a T-6, then it's a UFO!
                            MapAcft[rwyUpdate[i].pk].setIcon(UFO);
                        }
                        else { //It's a T-6...
                            MapAcft[rwyUpdate[i].pk].setIcon(legacyT6Icon);
                        }
                      }

                    OffStation.insertAdjacentHTML('beforeend',       
                    `<tr>
                    <th scope="row"><a href="dashboard/edit/${rwyUpdate[i].pk}" class="btn btn-primary btn-sm">edit</a></th>
                    <td>${rwyUpdate[i].pk.slice(-3)}</td>
                    <td>${rwyUpdate[i].fields.callSign}</td>
                    <td>${rwyUpdate[i].fields.alt_baro}</td>
                    <td>${rwyUpdate[i].fields.groundSpeed}</td>
                    <td>${String(rwyUpdate[i].fields.takeoffTime).slice(11, -8).concat(String(rwyUpdate[i].fields.takeoffTime).slice(23))}</td>
                    <td>${String(rwyUpdate[i].fields.landTime).slice(11, -8).concat(String(rwyUpdate[i].fields.landTime).slice(23))}</td>

                    <td style="padding-top: 0px; padding-bottom: 0px; white-space: nowrap;">
                        <table><tr><td>
                            <form method="POST" action="${window.location.href}/formX2/${rwyUpdate[i].pk}" class="form-group">    
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${formX2Checkmark}>  
                                <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">2-Ship</label>     
                            </form>
                        </td></tr>
                        <tr><td>
                            <form method="POST" action="${window.location.href}/formX4/${rwyUpdate[i].pk}" class="form-group">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${formX4Checkmark}>  
                                <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">4-Ship</label>
                            </form>
                        </td></tr></table>
                    </td>

                    <td>
                    <form method="POST" action="${window.location.href}/solo/${rwyUpdate[i].pk}" class="form-group">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                        <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${soloCheckmark}>  
                        <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">Solo</label>
                    </form>
                    </td>

                    <td><center><a href="dashboard/355/${rwyUpdate[i].pk}" class="btn btn-primary btn-sm btn-danger">355</a></center></td>
                    </tr>`
                    )
                }
                if (rwyUpdate[i].fields.state == "lost signal") {
                    if (!MapAcft[rwyUpdate[i].pk]) {
                        // If there is no marker with this id yet, instantiate a new one.;

                        if(rwyUpdate[i].fields.aircraftType != "TEX2") {
                            //If it's not a T-6, then it's a UFO!
                            MapAcft[rwyUpdate[i].pk] = L.marker([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude], {rotationAngle: rwyUpdate[i].fields.track, icon: inactiveUFO}).addTo(map).bindPopup(rwyUpdate[i].fields.callSign);
                        }
                        else { //It's a T-6...
                            MapAcft[rwyUpdate[i].pk] = L.marker([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude], {rotationAngle: rwyUpdate[i].fields.track, icon: inactiveLegacyT6Icon}).addTo(map).bindPopup(rwyUpdate[i].fields.callSign);
                        }
                          
                    } else {
                        // If there is already a marker with this id, simply modify its position.
                        MapAcft[rwyUpdate[i].pk].setLatLng([rwyUpdate[i].fields.latitude, rwyUpdate[i].fields.longitude]).setRotationAngle(rwyUpdate[i].fields.track).setPopupContent(rwyUpdate[i].fields.callSign);

                        if(rwyUpdate[i].fields.aircraftType != "TEX2") {
                            //If it's not a T-6, then it's a UFO!
                            MapAcft[rwyUpdate[i].pk].setIcon(inactiveUFO);
                        }
                        else { //It's a T-6...
                            MapAcft[rwyUpdate[i].pk].setIcon(inactiveLegacyT6Icon);
                        }
                      }

                    LostSignal.insertAdjacentHTML('beforeend',       
                    `<tr>
                    <th scope="row"><a href="dashboard/edit/${rwyUpdate[i].pk}" class="btn btn-primary btn-sm">edit</a></th>
                    <td>${rwyUpdate[i].pk.slice(-3)}</td>
                    <td>${rwyUpdate[i].fields.callSign}</td>
                    <td>${rwyUpdate[i].fields.alt_baro}</td>
                    <td>${rwyUpdate[i].fields.groundSpeed}</td>
                    <td>${String(rwyUpdate[i].fields.takeoffTime).slice(11, -8).concat(String(rwyUpdate[i].fields.takeoffTime).slice(23))}</td>
                    <td>${String(rwyUpdate[i].fields.landTime).slice(11, -8).concat(String(rwyUpdate[i].fields.landTime).slice(23))}</td>

                    <td style="padding-top: 0px; padding-bottom: 0px; white-space: nowrap;">
                        <table><tr><td>
                            <form method="POST" action="${window.location.href}/formX2/${rwyUpdate[i].pk}" class="form-group">    
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${formX2Checkmark}>  
                                <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">2-Ship</label>     
                            </form>
                        </td></tr>
                        <tr><td>
                            <form method="POST" action="${window.location.href}/formX4/${rwyUpdate[i].pk}" class="form-group">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${formX4Checkmark}>  
                                <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">4-Ship</label>
                            </form>
                        </td></tr></table>
                    </td>

                    <td>
                    <form method="POST" action="${window.location.href}/solo/${rwyUpdate[i].pk}" class="form-group">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                        <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${rwyUpdate[i].pk}" ${soloCheckmark}>  
                        <label class="form-check-label" for="flexCheck${rwyUpdate[i].pk}">Solo</label>
                    </form>
                    </td>

                    <td><center><a href="dashboard/355/${rwyUpdate[i].pk}" class="btn btn-primary btn-sm btn-danger">355</a></center></td>
                    </tr>`
                    )
                }
            }
                        //remove all aircraft on the map that were not in the update message
            for (const[tailNumber, data] of Object.entries(MapAcftNotUpdated)) {
                map.removeLayer(MapAcft[tailNumber])
                delete MapAcft[tailNumber]
            }

        }
    }
    )
}

// function removeAllChildNodes(parent) {
// while (parent.firstChild) {
//     parent.removeChild(parent.firstChild);
// }
// }