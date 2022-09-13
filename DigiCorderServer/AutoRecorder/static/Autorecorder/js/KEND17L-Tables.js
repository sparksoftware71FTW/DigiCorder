function loadKEND17L(chatSocket) {

    chatSocket.addEventListener('message', function(e){
        let data = JSON.parse(e.data)

        if(data.type == 't6Update'){

            let t6Update = JSON.parse(data.message)
            let t6Meta = JSON.parse(data.meta)
            console.log("HELLLOOOOOOOOOOOOOO")


            let KEND17LPattern = document.getElementById('KEND17L In Pattern')
            removeAllChildNodes(KEND17LPattern)
            let KEND17LTaxiing = document.getElementById('KEND17L Taxiing')
            removeAllChildNodes(KEND17LTaxiing)
            let KEND17LOffStation = document.getElementById('KEND17L Off Station')
            removeAllChildNodes(KEND17LOffStation)
            let KEND17LLostSignal = document.getElementById('KEND17L Lost Signal')
            removeAllChildNodes(KEND17LLostSignal)
            let numKEND17LPattern = document.getElementById('numKEND17L In Pattern')
            removeAllChildNodes(numKEND17LPattern)
            let numKEND17LTaxiing = document.getElementById('numKEND17L Taxiing')
            removeAllChildNodes(numKEND17LTaxiing)
            let numKEND17LOffStation = document.getElementById('numKEND17L Off Station')
            removeAllChildNodes(numKEND17LOffStation)
            let numKEND17LLostSignal = document.getElementById('numKEND17L Lost Signal')
            removeAllChildNodes(numKEND17LLostSignal)


            let KEND17Ldual145 = document.getElementById('KEND17L Dual Aircraft Outside the Pattern > 1+45')
            removeAllChildNodes(KEND17Ldual145)
            let KEND17Lsolo120 = document.getElementById('KEND17L Solo Aircraft Outside the Pattern > 1+20')
            removeAllChildNodes(KEND17Lsolo120)
            let KEND17LsolosOffStation = document.getElementById('KEND17L Solos Off Station')
            removeAllChildNodes(KEND17LsolosOffStation)
            let KEND17LsolosInPattern = document.getElementById('KEND17L Solos in the Pattern')
            removeAllChildNodes(KEND17LsolosInPattern)

            let numKEND17Ldual145 = document.getElementById('numKEND17L Dual Aircraft Outside the Pattern > 1+45')
            removeAllChildNodes(numKEND17Ldual145)
            let numKEND17Lsolo120 = document.getElementById('numKEND17L Solo Aircraft Outside the Pattern > 1+20')
            removeAllChildNodes(numKEND17Lsolo120)
            let numKEND17LsolosOffStation = document.getElementById('numKEND17L Solos Off Station')
            removeAllChildNodes(numKEND17LsolosOffStation)
            let numKEND17LsolosInPattern = document.getElementById('numKEND17L Solos in the Pattern')
            removeAllChildNodes(numKEND17LsolosInPattern)

            numKEND17Ldual145.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.dual145.length}</span>
            `)
            
            numKEND17Lsolo120.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.solo120.length}</span>
            `)
            
            numKEND17LsolosOffStation.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.solosOffStation.length}</span>
            `)
            
            numKEND17LsolosInPattern.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.solosInPattern.length}</span>
            `)

            //update the badge displaying the number of aircraft in each major state
            if(t6Meta.In_Pattern < 8) { //blue background
                numKEND17LPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-primary rounded-pill">${t6Meta.In_Pattern}</span>
                `)
            }
            else if (t6Meta.In_Pattern >= 12) { //red background
                numKEND17LPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-danger rounded-pill">${t6Meta.In_Pattern}</span>
                `)
            }
            else { //yellow background
                numKEND17LPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-warning rounded-pill">${t6Meta.In_Pattern}</span>
                `)
            }

            numKEND17LTaxiing.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.Taxiing}</span>
            `)

            numKEND17LOffStation.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.Off_Station}</span>
            `)

            numKEND17LLostSignal.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t6Meta.Lost_Signal}</span>
            `)

            for (let i = 0; i < t6Meta.dual145.length; i++) {
                KEND17Ldual145.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-secondary">${t6Meta.dual145[i]}</span>
                `
                )   
            }

            for (let i = 0; i < t6Meta.solo120.length; i++) {
                KEND17Lsolo120.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-danger">${t6Meta.solo120[i]}</span>
                `
                )   
            }

            for (let i = 0; i < t6Meta.solosOffStation.length; i++) {
                KEND17LsolosOffStation.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-warning">${t6Meta.solosOffStation[i]}</span>
                `
                )   
            }

            for (let i = 0; i < t6Meta.solosInPattern.length; i++) {
                KEND17LsolosInPattern.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-info">${t6Meta.solosInPattern[i]}</span>
                `
                )   
            }

            
            for (let i = 0; i < t6Update.length; i++) {

                if (t6Update[i].fields.state == "in pattern") {
                    KEND17LPattern.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="#" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t6Update[i].pk}</td>
                            <td>${t6Update[i].fields.callSign}</td>
                            <td>${t6Update[i].fields.alt_baro}</td>
                            <td>${t6Update[i].fields.groundSpeed}</td>
                            <td>${t6Update[i].fields.takeoffTime}</td>
                            <td>${t6Update[i].fields.landTime}</td>

                            <td>  
                                <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                                <label class="form-check-label" for="flexCheckDefault">Form Solo</label></td>
                            <td><a href="#" class="btn btn-primary btn-sm btn-danger">355</a></td>
                            </tr>`
                            )
                }
                if (t6Update[i].fields.state == "taxiing") {
                    KEND17LTaxiing.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="#" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t6Update[i].pk}</td>
                            <td>${t6Update[i].fields.callSign}</td>
                            <td>${t6Update[i].fields.alt_baro}</td>
                            <td>${t6Update[i].fields.groundSpeed}</td>
                            <td>${t6Update[i].fields.takeoffTime}</td>
                            <td>${t6Update[i].fields.landTime}</td>

                            <td>  
                                <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                                <label class="form-check-label" for="flexCheckDefault">Form Solo</label></td>
                            <td><a href="#" class="btn btn-primary btn-sm btn-danger">355</a></td>
                            </tr>`
                            )
                }
                if (t6Update[i].fields.state == "off station") {
                    KEND17LOffStation.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="#" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t6Update[i].pk}</td>
                            <td>${t6Update[i].fields.callSign}</td>
                            <td>${t6Update[i].fields.alt_baro}</td>
                            <td>${t6Update[i].fields.groundSpeed}</td>
                            <td>${t6Update[i].fields.takeoffTime}</td>
                            <td>${t6Update[i].fields.landTime}</td>

                            <td>  
                                <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                                <label class="form-check-label" for="flexCheckDefault">Form Solo</label></td>
                            <td><a href="#" class="btn btn-primary btn-sm btn-danger">355</a></td>
                            </tr>`
                            )
                }
                if (t6Update[i].fields.state == "lost signal") {
                    KEND17LLostSignal.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="#" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t6Update[i].pk}</td>
                            <td>${t6Update[i].fields.callSign}</td>
                            <td>${t6Update[i].fields.alt_baro}</td>
                            <td>${t6Update[i].fields.groundSpeed}</td>
                            <td>${t6Update[i].fields.takeoffTime}</td>
                            <td>${t6Update[i].fields.landTime}</td>

                            <td>  
                                <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                                <label class="form-check-label" for="flexCheckDefault">Form Solo</label></td>
                            <td><a href="#" class="btn btn-primary btn-sm btn-danger">355</a></td>
                            </tr>`
                            )
                }
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