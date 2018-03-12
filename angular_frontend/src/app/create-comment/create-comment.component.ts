import { Component, Input, Output, EventEmitter } from '@angular/core';
import { IssueService } from '../model/rest-services/issue.service';
import { MatDialog } from '@angular/material';

import { Issue } from '../model/issue/issue';
import { Comment } from '../model/issue/comment';
import { ErrorDialogueComponent } from '../error-dialogue/error-dialogue.component';

@Component({
	selector: 'app-create-comment',
	templateUrl: './create-comment.component.html',
	styleUrls: ['./create-comment.component.css']
})
export class CreateCommentComponent {

	@Input() issue: Issue;
	@Output("commentCreated") commentCreated: EventEmitter<Comment> = new EventEmitter();

	comment: string;

	constructor(private issueService: IssueService,
				private dialogue: MatDialog) { }

	submit() {
		this.issueService.addComment(this.issue, new Comment(this.comment)).subscribe(
			res => {
				this.commentCreated.emit(res);
				this.comment = ""
			},
			err => {
				this.dialogue.open(ErrorDialogueComponent, {
					'data': err
				});
			}
		);
	}

}
