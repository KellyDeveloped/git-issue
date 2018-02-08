import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { IssueListEntryComponent } from './issue-list-entry.component';

describe('IssueListEntryComponent', () => {
  let component: IssueListEntryComponent;
  let fixture: ComponentFixture<IssueListEntryComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ IssueListEntryComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(IssueListEntryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
