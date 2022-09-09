function loadKEND17R(chatSocket) {

    chatSocket.addEventListener('message', function(e){
        let data = JSON.parse(e.data)
        console.log('Data: ', data)
        console.log('Data.type: ', data.type)

        console.log('about to check data.type t38Update variable...')
        if(data.type == 't38Update'){

            let t38Update = JSON.parse(data.message)

            let KEND17RPattern = document.getElementById('KEND17R In Pattern')
            removeAllChildNodes(KEND17RPattern)
            let KEND17RTaxiing = document.getElementById('KEND17R Taxiing')
            removeAllChildNodes(KEND17RTaxiing)
            let KEND17ROffStation = document.getElementById('KEND17R Off Station')
            removeAllChildNodes(KEND17ROffStation)
            let KEND17RLostSignal = document.getElementById('KEND17R Lost Signal')
            removeAllChildNodes(KEND17RLostSignal)



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
//     while (parent.firstChild) {
//         parent.removeChild(parent.firstChild);
//     }
// }