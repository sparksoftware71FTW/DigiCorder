var KEND35Lmap = L.map('KEND35Lmap').setView([36.3393, -97.9131], 10);


function rxNextTOMessageKEND35L(chatSocket) {

    chatSocket.addEventListener('message', function(e){

        let msg = JSON.parse(e.data)

        console.log("runway is: ")
        console.log(msg.runway)
        if(msg.type == 'nextTOMessage' && msg.runway == "KEND 35L/17R"){
            console.log("We made it")

                let data = msg.data
                document.getElementById('nextTO-KEND35L-solo').checked = data.solo
                document.getElementById('nextTO-KEND35L-formationX2').checked = data.formationX2
                document.getElementById('nextTO-KEND35L-formationX4').checked = data.formationX4
        }
    })
}

function nextTOMessageKEND35L(chatSocket, id) {
    solo = document.getElementById('nextTO-KEND35L-solo').checked
    formationX2 = document.getElementById('nextTO-KEND35L-formationX2').checked
    formationX4 = document.getElementById('nextTO-KEND35L-formationX4').checked

    if(formationX2 == true && id == 'formationX4') {
        formationX4 = false
    }

    if(formationX4 == true && id == 'formationX2') {
        formationX2 = false
    }

    chatSocket.send(JSON.stringify({
      'type': 'nextTOMessage',
      'runway': 'KEND 35L/17R',
      'data': {
        'solo': solo,
        'formationX2': formationX2,
        'formationX4': formationX4
      }
  }))
}

function loadKEND35L(chatSocket, csrf_token) {

    //var KEND35Lmap = L.map('KEND35Lmap').setView([36.3393, -97.9131], 13);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(KEND35Lmap);

    L.marker([36.3393, -97.9131]).addTo(KEND35Lmap)
        .bindPopup('KEND')
        .openPopup();

    var KEND35LMapAcft = {}
    var KEND35LMapAcftNotUpdated = []

    let T38Icon = L.icon({
        iconUrl: '../static/AutoRecorder/images/Black T-38 Silhouette with Alpha.png',
        //shadowUrl: '../static/AutoRecorder/leaflet/images/marker-shadow.png',

        iconSize:     [40, 40], // size of the icon
        shadowSize:   [20, 20], // size of the shadow
        iconAnchor:   [20, 20], // point of the icon which will correspond to marker's location
        shadowAnchor: [0, 0],  // the same for the shadow
        popupAnchor:  [0, -30] // point from which the popup should open relative to the iconAnchor

    })

    let inactiveT38Icon = L.icon({
        iconUrl: '../static/AutoRecorder/images/30-Black T-38 Silhouette with Alpha.png',
        //shadowUrl: '../static/AutoRecorder/leaflet/images/marker-shadow.png',

        iconSize:     [40, 40], // size of the icon
        shadowSize:   [20, 20], // size of the shadow
        iconAnchor:   [20, 20], // point of the icon which will correspond to marker's location
        shadowAnchor: [0, 0],  // the same for the shadow
        popupAnchor:  [0, -30] // point from which the popup should open relative to the iconAnchor

    })

    let UFO = L.icon({
        iconUrl: '../static/AutoRecorder/images/UFO.png',
        //shadowUrl: '../static/AutoRecorder/leaflet/images/marker-shadow.png',

        iconSize:     [20, 20], // size of the icon
        shadowSize:   [20, 20], // size of the shadow
        iconAnchor:   [10, 10], // point of the icon which will correspond to marker's location
        shadowAnchor: [0, 0],  // the same for the shadow
        popupAnchor:  [0, -30] // point from which the popup should open relative to the iconAnchor

    })

    let inactiveUFO = L.icon({
        iconUrl: '../static/AutoRecorder/images/30-UFO.png',
        //shadowUrl: '../static/AutoRecorder/leaflet/images/marker-shadow.png',

        iconSize:     [30, 30], // size of the icon
        shadowSize:   [20, 20], // size of the shadow
        iconAnchor:   [15, 15], // point of the icon which will correspond to marker's location
        shadowAnchor: [0, 0],  // the same for the shadow
        popupAnchor:  [0, -30] // point from which the popup should open relative to the iconAnchor

    })

    
    chatSocket.addEventListener('message', function(e){
        let data = JSON.parse(e.data)

        if(data.type == 't38Update'){

            let t38Update = JSON.parse(data.message)
            let t38Meta = JSON.parse(data.meta)
            console.log("HELLLOOOOOOOOOOOOOO")


            let KEND35LPattern = document.getElementById('KEND35L In Pattern')
            removeAllChildNodes(KEND35LPattern)
            let KEND35LTaxiing = document.getElementById('KEND35L Taxiing')
            removeAllChildNodes(KEND35LTaxiing)
            let KEND35LOffStation = document.getElementById('KEND35L Off Station')
            removeAllChildNodes(KEND35LOffStation)
            let KEND35LLostSignal = document.getElementById('KEND35L Lost Signal')
            removeAllChildNodes(KEND35LLostSignal)
            let numKEND35LPattern = document.getElementById('numKEND35L In Pattern')
            removeAllChildNodes(numKEND35LPattern)
            let numKEND35LTaxiing = document.getElementById('numKEND35L Taxiing')
            removeAllChildNodes(numKEND35LTaxiing)
            let numKEND35LOffStation = document.getElementById('numKEND35L Off Station')
            removeAllChildNodes(numKEND35LOffStation)
            let numKEND35LLostSignal = document.getElementById('numKEND35L Lost Signal')
            removeAllChildNodes(numKEND35LLostSignal)


            let KEND35Ldual120 = document.getElementById('KEND35L Dual Aircraft Outside the Pattern > 1+20')
            removeAllChildNodes(KEND35Ldual120)
            let KEND35Lsolo100 = document.getElementById('KEND35L Solo Aircraft Outside the Pattern > 1+00')
            removeAllChildNodes(KEND35Lsolo100)
            let KEND35LsolosOffStation = document.getElementById('KEND35L Solos Off Station')
            removeAllChildNodes(KEND35LsolosOffStation)
            let KEND35LsolosInPattern = document.getElementById('KEND35L Solos in the Pattern')
            removeAllChildNodes(KEND35LsolosInPattern)

            let numKEND35Ldual120 = document.getElementById('numKEND35L Dual Aircraft Outside the Pattern > 1+20')
            removeAllChildNodes(numKEND35Ldual120)
            let numKEND35Lsolo100 = document.getElementById('numKEND35L Solo Aircraft Outside the Pattern > 1+00')
            removeAllChildNodes(numKEND35Lsolo100)
            let numKEND35LsolosOffStation = document.getElementById('numKEND35L Solos Off Station')
            removeAllChildNodes(numKEND35LsolosOffStation)
            let numKEND35LsolosInPattern = document.getElementById('numKEND35L Solos in the Pattern')
            removeAllChildNodes(numKEND35LsolosInPattern)

            numKEND35Ldual120.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.dual120.length}</span>
            `)
            
            numKEND35Lsolo100.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.solo100.length}</span>
            `)
            
            numKEND35LsolosOffStation.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.solosOffStation.length}</span>
            `)
            
            numKEND35LsolosInPattern.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.solosInPattern.length}</span>
            `)

            //update the badge displaying the number of aircraft in each major state
            if(t38Meta.In_Pattern < 8) { //blue background
                numKEND35LPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-primary rounded-pill">${t38Meta.In_Pattern}</span>
                `)
            }
            else if (t38Meta.In_Pattern >= 12) { //red background
                numKEND35LPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-danger rounded-pill">${t38Meta.In_Pattern}</span>
                `)
            }
            else { //yellow background
                numKEND35LPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-warning rounded-pill">${t38Meta.In_Pattern}</span>
                `)
            }

            numKEND35LTaxiing.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.Taxiing}</span>
            `)

            numKEND35LOffStation.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.Off_Station}</span>
            `)

            numKEND35LLostSignal.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.Lost_Signal}</span>
            `)

            for (let i = 0; i < t38Meta.dual120.length; i++) {
                KEND35Ldual120.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-secondary">${t38Meta.dual120[i]}</span>
                `
                )   
            }

            for (let i = 0; i < t38Meta.solo100.length; i++) {
                KEND35Lsolo100.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-danger">${t38Meta.solo100[i]}</span>
                `
                )   
            }

            for (let i = 0; i < t38Meta.solosOffStation.length; i++) {
                KEND35LsolosOffStation.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-warning">${t38Meta.solosOffStation[i]}</span>
                `
                )   
            }

            for (let i = 0; i < t38Meta.solosInPattern.length; i++) {
                KEND35LsolosInPattern.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-info">${t38Meta.solosInPattern[i]}</span>
                `
                )   
            }

            KEND35LMapAcftNotUpdated = {...KEND35LMapAcft}
            console.log(KEND35LMapAcftNotUpdated)
                            
            for (let i = 0; i < t38Update.length; i++) {

                delete KEND35LMapAcftNotUpdated[t38Update[i].pk]

                let formX2Checkmark = ""
                let formX4Checkmark = ""
                let soloCheckmark = ""
                if (t38Update[i].fields.solo) {soloCheckmark = "checked"}
                if (t38Update[i].fields.formationX2) {formX2Checkmark = "checked"}
                if (t38Update[i].fields.formationX4) {formX4Checkmark = "checked"}
                

                if (t38Update[i].fields.substate == "shoehorn") {
                    if (!KEND35LMapAcft[t38Update[i].pk]) {
                        // If there is no marker with this id yet, instantiate a new one.;

                        if(t38Update[i].fields.aircraftType != "T38") {
                            //If it's not a T-38, then it's a UFO!
                            KEND35LMapAcft[t38Update[i].pk] = L.marker([t38Update[i].fields.latitude, t38Update[i].fields.longitude], {rotationAngle: t38Update[i].fields.track, icon: UFO}).addTo(KEND35Lmap).bindPopup(t38Update[i].fields.callSign);
                        }
                        else { //It's a T-38...
                            KEND35LMapAcft[t38Update[i].pk] = L.marker([t38Update[i].fields.latitude, t38Update[i].fields.longitude], {rotationAngle: t38Update[i].fields.track, icon: T38Icon}).addTo(KEND35Lmap).bindPopup(t38Update[i].fields.callSign);
                        }
                          
                      } else {
                        // If there is already a marker with this id, simply modify its position.
                        KEND35LMapAcft[t38Update[i].pk].setLatLng([t38Update[i].fields.latitude, t38Update[i].fields.longitude]).setRotationAngle(t38Update[i].fields.track).setPopupContent(t38Update[i].fields.callSign);

                        if(t38Update[i].fields.aircraftType != "T38") {
                            //If it's not a T-38, then it's a UFO!
                            KEND35LMapAcft[t38Update[i].pk].setIcon(UFO);
                        }
                        else { //It's a T-38...
                            KEND35LMapAcft[t38Update[i].pk].setIcon(T38Icon);
                        }

                      }

                    KEND35LPattern.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="dashboard/edit/${t38Update[i].pk}" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t38Update[i].pk.slice(-3)}</td>
                            <td>${t38Update[i].fields.callSign}</td>
                            <td>${t38Update[i].fields.alt_baro}</td>
                            <td>${t38Update[i].fields.groundSpeed}</td>
                            <td>${String(t38Update[i].fields.takeoffTime).slice(11, -8).concat(String(t38Update[i].fields.takeoffTime).slice(23))}</td>
                            <td>${String(t38Update[i].fields.landTime).slice(11, -8).concat(String(t38Update[i].fields.landTime).slice(23))}</td>

                            <td style="padding-top: 0px; padding-bottom: 0px; white-space: nowrap;">
                                <table><tr><td>
                                    <form method="POST" action="dashboard/formX2/${t38Update[i].pk}" class="form-group">    
                                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                        <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${t38Update[i].pk}" ${formX2Checkmark}>  
                                        <label class="form-check-label" for="flexCheck${t38Update[i].pk}">2-Ship</label>     
                                    </form>
                                </td></tr>
                                <tr><td>
                                    <form method="POST" action="dashboard/formX4/${t38Update[i].pk}" class="form-group">
                                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                        <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${t38Update[i].pk}" ${formX4Checkmark}>  
                                        <label class="form-check-label" for="flexCheck${t38Update[i].pk}">4-Ship</label>
                                    </form>
                                </td></tr></table>
                            </td>

                            <td>
                            <form method="POST" action="dashboard/solo/${t38Update[i].pk}" class="form-group">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${t38Update[i].pk}" ${soloCheckmark}>  
                                <label class="form-check-label" for="flexCheck${t38Update[i].pk}">Solo</label>
                            </form>
                            </td>

                            <td><center><a href="dashboard/355/${t38Update[i].pk}" class="btn btn-primary btn-sm btn-danger">355</a></center></td>
                            </tr>`
                            )

                }
                if (t38Update[i].fields.state == "taxiing") {
                    if (!KEND35LMapAcft[t38Update[i].pk]) {
                        // If there is no marker with this id yet, instantiate a new one.;

                        if(t38Update[i].fields.aircraftType != "T38") {
                            //If it's not a T-38, then it's a UFO!
                            KEND35LMapAcft[t38Update[i].pk] = L.marker([t38Update[i].fields.latitude, t38Update[i].fields.longitude], {rotationAngle: t38Update[i].fields.track, icon: inactiveUFO}).addTo(KEND35Lmap).bindPopup(t38Update[i].fields.callSign);
                        }
                        else { //It's a T-38...
                            KEND35LMapAcft[t38Update[i].pk] = L.marker([t38Update[i].fields.latitude, t38Update[i].fields.longitude], {rotationAngle: t38Update[i].fields.track, icon: inactiveT38Icon}).addTo(KEND35Lmap).bindPopup(t38Update[i].fields.callSign);
                        }
                          
                    } else {
                        // If there is already a marker with this id, simply modify its position.
                        KEND35LMapAcft[t38Update[i].pk].setLatLng([t38Update[i].fields.latitude, t38Update[i].fields.longitude]).setRotationAngle(t38Update[i].fields.track).setPopupContent(t38Update[i].fields.callSign);

                        if(t38Update[i].fields.aircraftType != "T38") {
                            //If it's not a T-38, then it's a UFO!
                            KEND35LMapAcft[t38Update[i].pk].setIcon(inactiveUFO);
                        }
                        else { //It's a T-38...
                            KEND35LMapAcft[t38Update[i].pk].setIcon(inactiveT38Icon);
                        }

                      }

                    KEND35LTaxiing.insertAdjacentHTML('beforeend',       
                    `<tr>
                    <th scope="row"><a href="dashboard/edit/${t38Update[i].pk}" class="btn btn-primary btn-sm">edit</a></th>
                    <td>${t38Update[i].pk.slice(-3)}</td>
                    <td>${t38Update[i].fields.callSign}</td>
                    <td>${t38Update[i].fields.alt_baro}</td>
                    <td>${t38Update[i].fields.groundSpeed}</td>
                    <td>${String(t38Update[i].fields.takeoffTime).slice(11, -8).concat(String(t38Update[i].fields.takeoffTime).slice(23))}</td>
                    <td>${String(t38Update[i].fields.landTime).slice(11, -8).concat(String(t38Update[i].fields.landTime).slice(23))}</td>

                    <td style="padding-top: 0px; padding-bottom: 0px; white-space: nowrap;">
                        <table><tr><td>
                            <form method="POST" action="dashboard/formX2/${t38Update[i].pk}" class="form-group">    
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${t38Update[i].pk}" ${formX2Checkmark}>  
                                <label class="form-check-label" for="flexCheck${t38Update[i].pk}">2-Ship</label>     
                            </form>
                        </td></tr>
                        <tr><td>
                            <form method="POST" action="dashboard/formX4/${t38Update[i].pk}" class="form-group">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${t38Update[i].pk}" ${formX4Checkmark}>  
                                <label class="form-check-label" for="flexCheck${t38Update[i].pk}">4-Ship</label>
                            </form>
                        </td></tr></table>
                    </td>

                    <td>
                    <form method="POST" action="dashboard/solo/${t38Update[i].pk}" class="form-group">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                        <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${t38Update[i].pk}" ${soloCheckmark}>  
                        <label class="form-check-label" for="flexCheck${t38Update[i].pk}">Solo</label>
                    </form>
                    </td>

                    <td><center><a href="dashboard/355/${t38Update[i].pk}" class="btn btn-primary btn-sm btn-danger">355</a></center></td>
                    </tr>`
                    )
                }
                if (t38Update[i].fields.state == "off station") {
                    if (!KEND35LMapAcft[t38Update[i].pk]) {
                        // If there is no marker with this id yet, instantiate a new one.;

                        if(t38Update[i].fields.aircraftType != "T38") {
                            //If it's not a T-38, then it's a UFO!
                            KEND35LMapAcft[t38Update[i].pk] = L.marker([t38Update[i].fields.latitude, t38Update[i].fields.longitude], {rotationAngle: t38Update[i].fields.track, icon: UFO}).addTo(KEND35Lmap).bindPopup(t38Update[i].fields.callSign);
                        }
                        else { //It's a T-38...
                            KEND35LMapAcft[t38Update[i].pk] = L.marker([t38Update[i].fields.latitude, t38Update[i].fields.longitude], {rotationAngle: t38Update[i].fields.track, icon: T38Icon}).addTo(KEND35Lmap).bindPopup(t38Update[i].fields.callSign);
                        }
                          
                    } else {
                        // If there is already a marker with this id, simply modify its position.
                        KEND35LMapAcft[t38Update[i].pk].setLatLng([t38Update[i].fields.latitude, t38Update[i].fields.longitude]).setRotationAngle(t38Update[i].fields.track).setPopupContent(t38Update[i].fields.callSign);

                        if(t38Update[i].fields.aircraftType != "T38") {
                            //If it's not a T-38, then it's a UFO!
                            KEND35LMapAcft[t38Update[i].pk].setIcon(UFO);
                        }
                        else { //It's a T-38...
                            KEND35LMapAcft[t38Update[i].pk].setIcon(T38Icon);
                        }

                      }

                    KEND35LOffStation.insertAdjacentHTML('beforeend',       
                    `<tr>
                    <th scope="row"><a href="dashboard/edit/${t38Update[i].pk}" class="btn btn-primary btn-sm">edit</a></th>
                    <td>${t38Update[i].pk.slice(-3)}</td>
                    <td>${t38Update[i].fields.callSign}</td>
                    <td>${t38Update[i].fields.alt_baro}</td>
                    <td>${t38Update[i].fields.groundSpeed}</td>
                    <td>${String(t38Update[i].fields.takeoffTime).slice(11, -8).concat(String(t38Update[i].fields.takeoffTime).slice(23))}</td>
                    <td>${String(t38Update[i].fields.landTime).slice(11, -8).concat(String(t38Update[i].fields.landTime).slice(23))}</td>

                    <td style="padding-top: 0px; padding-bottom: 0px; white-space: nowrap;">
                        <table><tr><td>
                            <form method="POST" action="dashboard/formX2/${t38Update[i].pk}" class="form-group">    
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${t38Update[i].pk}" ${formX2Checkmark}>  
                                <label class="form-check-label" for="flexCheck${t38Update[i].pk}">2-Ship</label>     
                            </form>
                        </td></tr>
                        <tr><td>
                            <form method="POST" action="dashboard/formX4/${t38Update[i].pk}" class="form-group">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${t38Update[i].pk}" ${formX4Checkmark}>  
                                <label class="form-check-label" for="flexCheck${t38Update[i].pk}">4-Ship</label>
                            </form>
                        </td></tr></table>
                    </td>

                    <td>
                    <form method="POST" action="dashboard/solo/${t38Update[i].pk}" class="form-group">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                        <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${t38Update[i].pk}" ${soloCheckmark}>  
                        <label class="form-check-label" for="flexCheck${t38Update[i].pk}">Solo</label>
                    </form>
                    </td>

                    <td><center><a href="dashboard/355/${t38Update[i].pk}" class="btn btn-primary btn-sm btn-danger">355</a></center></td>
                    </tr>`
                    )
                }
                if (t38Update[i].fields.state == "lost signal") {
                    if (!KEND35LMapAcft[t38Update[i].pk]) {
                        // If there is no marker with this id yet, instantiate a new one.;

                        if(t38Update[i].fields.aircraftType != "T38") {
                            //If it's not a T-38, then it's a UFO!
                            KEND35LMapAcft[t38Update[i].pk] = L.marker([t38Update[i].fields.latitude, t38Update[i].fields.longitude], {rotationAngle: t38Update[i].fields.track, icon: inactiveUFO}).addTo(KEND35Lmap).bindPopup(t38Update[i].fields.callSign);
                        }
                        else { //It's a T-38...
                            KEND35LMapAcft[t38Update[i].pk] = L.marker([t38Update[i].fields.latitude, t38Update[i].fields.longitude], {rotationAngle: t38Update[i].fields.track, icon: inactiveT38Icon}).addTo(KEND35Lmap).bindPopup(t38Update[i].fields.callSign);
                        }
                          
                    } else {
                        // If there is already a marker with this id, simply modify its position.
                        KEND35LMapAcft[t38Update[i].pk].setLatLng([t38Update[i].fields.latitude, t38Update[i].fields.longitude]).setRotationAngle(t38Update[i].fields.track).setPopupContent(t38Update[i].fields.callSign);

                        if(t38Update[i].fields.aircraftType != "T38") {
                            //If it's not a T-38, then it's a UFO!
                            KEND35LMapAcft[t38Update[i].pk].setIcon(inactiveUFO);
                        }
                        else { //It's a T-38...
                            KEND35LMapAcft[t38Update[i].pk].setIcon(inactiveT38Icon);
                        }

                      }

                    KEND35LLostSignal.insertAdjacentHTML('beforeend',       
                    `<tr>
                    <th scope="row"><a href="dashboard/edit/${t38Update[i].pk}" class="btn btn-primary btn-sm">edit</a></th>
                    <td>${t38Update[i].pk.slice(-3)}</td>
                    <td>${t38Update[i].fields.callSign}</td>
                    <td>${t38Update[i].fields.alt_baro}</td>
                    <td>${t38Update[i].fields.groundSpeed}</td>
                    <td>${String(t38Update[i].fields.takeoffTime).slice(11, -8).concat(String(t38Update[i].fields.takeoffTime).slice(23))}</td>
                    <td>${String(t38Update[i].fields.landTime).slice(11, -8).concat(String(t38Update[i].fields.landTime).slice(23))}</td>

                    <td style="padding-top: 0px; padding-bottom: 0px; white-space: nowrap;">
                        <table><tr><td>
                            <form method="POST" action="dashboard/formX2/${t38Update[i].pk}" class="form-group">    
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${t38Update[i].pk}" ${formX2Checkmark}>  
                                <label class="form-check-label" for="flexCheck${t38Update[i].pk}">2-Ship</label>     
                            </form>
                        </td></tr>
                        <tr><td>
                            <form method="POST" action="dashboard/formX4/${t38Update[i].pk}" class="form-group">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                                <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${t38Update[i].pk}" ${formX4Checkmark}>  
                                <label class="form-check-label" for="flexCheck${t38Update[i].pk}">4-Ship</label>
                            </form>
                        </td></tr></table>
                    </td>

                    <td>
                    <form method="POST" action="dashboard/solo/${t38Update[i].pk}" class="form-group">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrf_token}">
                        <input onChange="this.form.submit()" class="form-check-input" type="checkbox" value="" id="flexCheck${t38Update[i].pk}" ${soloCheckmark}>  
                        <label class="form-check-label" for="flexCheck${t38Update[i].pk}">Solo</label>
                    </form>
                    </td>

                    <td><center><a href="dashboard/355/${t38Update[i].pk}" class="btn btn-primary btn-sm btn-danger">355</a></center></td>
                    </tr>`
                    )
                }
            }
                        //remove all aircraft on the map that were not in the update message
            for (const[tailNumber, data] of Object.entries(KEND35LMapAcftNotUpdated)) {
                KEND35Lmap.removeLayer(KEND35LMapAcft[tailNumber])
                delete KEND35LMapAcft[tailNumber]
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