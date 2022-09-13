function loadKEND17R(chatSocket) {

    chatSocket.addEventListener('message', function(e){
        let data = JSON.parse(e.data)

        if(data.type == 't38Update'){

            let t38Update = JSON.parse(data.message)
            let t38Meta = JSON.parse(data.meta)
            console.log("HELLLOOOOOOOOOOOOOO")


            let KEND17RPattern = document.getElementById('KEND17R In Pattern')
            removeAllChildNodes(KEND17RPattern)
            let KEND17RTaxiing = document.getElementById('KEND17R Taxiing')
            removeAllChildNodes(KEND17RTaxiing)
            let KEND17ROffStation = document.getElementById('KEND17R Off Station')
            removeAllChildNodes(KEND17ROffStation)
            let KEND17RLostSignal = document.getElementById('KEND17R Lost Signal')
            removeAllChildNodes(KEND17RLostSignal)
            let numKEND17RPattern = document.getElementById('numKEND17R In Pattern')
            removeAllChildNodes(numKEND17RPattern)
            let numKEND17RTaxiing = document.getElementById('numKEND17R Taxiing')
            removeAllChildNodes(numKEND17RTaxiing)
            let numKEND17ROffStation = document.getElementById('numKEND17R Off Station')
            removeAllChildNodes(numKEND17ROffStation)
            let numKEND17RLostSignal = document.getElementById('numKEND17R Lost Signal')
            removeAllChildNodes(numKEND17RLostSignal)


            let KEND17Rdual145 = document.getElementById('KEND17R Dual Aircraft Outside the Pattern > 1+45')
            removeAllChildNodes(KEND17Rdual145)
            let KEND17Rsolo120 = document.getElementById('KEND17R Solo Aircraft Outside the Pattern > 1+20')
            removeAllChildNodes(KEND17Rsolo120)
            let KEND17RsolosOffStation = document.getElementById('KEND17R Solos Off Station')
            removeAllChildNodes(KEND17RsolosOffStation)
            let KEND17RsolosInPattern = document.getElementById('KEND17R Solos in the Pattern')
            removeAllChildNodes(KEND17RsolosInPattern)

            let numKEND17Rdual145 = document.getElementById('numKEND17R Dual Aircraft Outside the Pattern > 1+45')
            removeAllChildNodes(numKEND17Rdual145)
            let numKEND17Rsolo120 = document.getElementById('numKEND17R Solo Aircraft Outside the Pattern > 1+20')
            removeAllChildNodes(numKEND17Rsolo120)
            let numKEND17RsolosOffStation = document.getElementById('numKEND17R Solos Off Station')
            removeAllChildNodes(numKEND17RsolosOffStation)
            let numKEND17RsolosInPattern = document.getElementById('numKEND17R Solos in the Pattern')
            removeAllChildNodes(numKEND17RsolosInPattern)

            numKEND17Rdual145.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.dual145.length}</span>
            `)
            
            numKEND17Rsolo120.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.solo120.length}</span>
            `)
            
            numKEND17RsolosOffStation.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.solosOffStation.length}</span>
            `)
            
            numKEND17RsolosInPattern.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.solosInPattern.length}</span>
            `)

            //update the badge displaying the number of aircraft in each major state
            if(t38Meta.In_Pattern < 8) { //blue background
                numKEND17RPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-primary rounded-pill">${t38Meta.In_Pattern}</span>
                `)
            }
            else if (t38Meta.In_Pattern >= 12) { //red background
                numKEND17RPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-danger rounded-pill">${t38Meta.In_Pattern}</span>
                `)
            }
            else { //yellow background
                numKEND17RPattern.insertAdjacentHTML('beforeend', `
                <span class="badge bg-warning rounded-pill">${t38Meta.In_Pattern}</span>
                `)
            }

            numKEND17RTaxiing.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.Taxiing}</span>
            `)

            numKEND17ROffStation.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.Off_Station}</span>
            `)

            numKEND17RLostSignal.insertAdjacentHTML('beforeend', `
            <span class="badge bg-primary rounded-pill">${t38Meta.Lost_Signal}</span>
            `)

            for (let i = 0; i < t38Meta.dual145.length; i++) {
                KEND17Rdual145.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-secondary">${t38Meta.dual145[i]}</span>
                `
                )   
            }

            for (let i = 0; i < t38Meta.solo120.length; i++) {
                KEND17Rsolo120.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-danger">${t38Meta.solo120[i]}</span>
                `
                )   
            }

            for (let i = 0; i < t38Meta.solosOffStation.length; i++) {
                KEND17RsolosOffStation.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-warning">${t38Meta.solosOffStation[i]}</span>
                `
                )   
            }

            for (let i = 0; i < t38Meta.solosInPattern.length; i++) {
                KEND17RsolosInPattern.insertAdjacentHTML('beforeend', `
                <span class="badge text-bg-info">${t38Meta.solosInPattern[i]}</span>
                `
                )   
            }

            
            for (let i = 0; i < t38Update.length; i++) {

                if (t38Update[i].fields.state == "in pattern") {
                    KEND17RPattern.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="#" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t38Update[i].pk}</td>
                            <td>${t38Update[i].fields.callSign}</td>
                            <td>${t38Update[i].fields.alt_baro}</td>
                            <td>${t38Update[i].fields.groundSpeed}</td>
                            <td>${t38Update[i].fields.takeoffTime}</td>
                            <td>${t38Update[i].fields.landTime}</td>

                            <td>  
                                <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                                <label class="form-check-label" for="flexCheckDefault">Form Solo</label></td>
                            <td><a href="#" class="btn btn-primary btn-sm btn-danger">355</a></td>
                            </tr>`
                            )
                }
                if (t38Update[i].fields.state == "taxiing") {
                    KEND17RTaxiing.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="#" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t38Update[i].pk}</td>
                            <td>${t38Update[i].fields.callSign}</td>
                            <td>${t38Update[i].fields.alt_baro}</td>
                            <td>${t38Update[i].fields.groundSpeed}</td>
                            <td>${t38Update[i].fields.takeoffTime}</td>
                            <td>${t38Update[i].fields.landTime}</td>

                            <td>  
                                <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                                <label class="form-check-label" for="flexCheckDefault">Form Solo</label></td>
                            <td><a href="#" class="btn btn-primary btn-sm btn-danger">355</a></td>
                            </tr>`
                            )
                }
                if (t38Update[i].fields.state == "off station") {
                    KEND17ROffStation.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="#" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t38Update[i].pk}</td>
                            <td>${t38Update[i].fields.callSign}</td>
                            <td>${t38Update[i].fields.alt_baro}</td>
                            <td>${t38Update[i].fields.groundSpeed}</td>
                            <td>${t38Update[i].fields.takeoffTime}</td>
                            <td>${t38Update[i].fields.landTime}</td>

                            <td>  
                                <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                                <label class="form-check-label" for="flexCheckDefault">Form Solo</label></td>
                            <td><a href="#" class="btn btn-primary btn-sm btn-danger">355</a></td>
                            </tr>`
                            )
                }
                if (t38Update[i].fields.state == "lost signal") {
                    KEND17RLostSignal.insertAdjacentHTML('beforeend',       
                            `<tr>
                            <th scope="row"><a href="#" class="btn btn-primary btn-sm">edit</a></th>
                            <td>${t38Update[i].pk}</td>
                            <td>${t38Update[i].fields.callSign}</td>
                            <td>${t38Update[i].fields.alt_baro}</td>
                            <td>${t38Update[i].fields.groundSpeed}</td>
                            <td>${t38Update[i].fields.takeoffTime}</td>
                            <td>${t38Update[i].fields.landTime}</td>

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