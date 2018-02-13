import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material';

@Component({
  selector: 'app-error-dialogue',
  templateUrl: './error-dialogue.component.html',
  styleUrls: ['./error-dialogue.component.css']
})
export class ErrorDialogueComponent {

	constructor(@Inject(MAT_DIALOG_DATA) public data: any) {

	}

}
