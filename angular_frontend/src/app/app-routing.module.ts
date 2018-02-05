import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { SingleIssueComponent } from './single-issue/single-issue.component'
import { IssueListComponent } from './issue-list/issue-list.component'
import { EditIssueComponent } from './edit-issue/edit-issue.component'
import { CreateIssueComponent } from './create-issue/create-issue.component'

const routes: Routes = [
  { path: "issues", component: IssueListComponent },
  { path: "issues/create", component: CreateIssueComponent },
  { path: "issues/:id", component: SingleIssueComponent },
  { path: "issues/:id/edit", component: EditIssueComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
