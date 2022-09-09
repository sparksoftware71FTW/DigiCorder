function loadKEND17L(chatSocket) {

    chatSocket.addEventListener('message', function(e){
        let data = JSON.parse(e.data)

        if(data.type == 't6Update'){

            t6Update = JSON.parse(data.message)

            let KEND17LPattern = document.getElementById('KEND17L In Pattern')
            removeAllChildNodes(KEND17LPattern)
            let KEND17LTaxiing = document.getElementById('KEND17L Taxiing')
            removeAllChildNodes(KEND17LTaxiing)
            let KEND17LOffStation = document.getElementById('KEND17L Off Station')
            removeAllChildNodes(KEND17LOffStation)
            let KEND17LLostSignal = document.getElementById('KEND17L Lost Signal')
            removeAllChildNodes(KEND17LLostSignal)

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